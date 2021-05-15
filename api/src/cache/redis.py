import json
from functools import wraps
from socket import gaierror
from typing import Optional, List, Callable
from uuid import UUID

import backoff
from aioredis import Redis
from fastapi import Request

from cache.abstract import Cache
from db import redis

exceptions_list = (gaierror,)
DEFAULT_TTL = 60


def default_response_keybuilder(func, query_args, *args, **kwargs) -> str:
    """
    Формирует ключ для хранения ответа на запрос в кеше.
    Если среди параметров функции есть объект Response, использует
    query_args для формирования ключа (для функций, которые используют
    Response для получения параметров запроса)
    """
    kwargs_key = {k: v for k, v in kwargs.items() if k in query_args}
    for k, v in kwargs.items():
        if isinstance(v, Request):
            kwargs_key['query_params'] = v.query_params
    return f'response:{func.__module__}.{func.__name__}:{args}:{kwargs_key}'


@backoff.on_exception(backoff.expo, exceptions_list, max_tries=10)
def cache_response(
        ttl: Optional[int] = DEFAULT_TTL,
        query_args: List[str] = [],
        key_builder: Callable = default_response_keybuilder,
):
    """
    Декоратор для кеширования ответа метода API

    ttl: время жизни записи в кеш
    query_args: аргументы метода API, которые меняют его поведение
    """

    def wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            nonlocal ttl
            nonlocal query_args

            cache = await redis.get_redis()
            cache_key = key_builder(func, query_args, *args, **kwargs)
            resp = await cache.get(cache_key)
            if resp:
                return json.loads(resp)
            ret = await func(*args, **kwargs)
            await cache.set(cache_key, ret.json(), expire=ttl)
            return ret

        return inner

    return wrapper


class RedisCache(Cache):
    """
    Redis-кеш для объектов. Ничего не знает об их структуре,
    просто сохраняет и возвращает стороки из редиса.
    """

    def __init__(self, redis: Redis, keybuilder: Callable[[UUID], str], ttl: int = DEFAULT_TTL):
        self.redis = redis
        self.keybuilder = keybuilder
        self.ttl = ttl

    @backoff.on_exception(backoff.expo, exceptions_list, max_tries=10)
    async def get(self, obj_id: UUID) -> Optional[str]:
        resp = await self.redis.get(self.keybuilder(obj_id))
        if not resp:
            return None

        return resp

    @backoff.on_exception(backoff.expo, exceptions_list, max_tries=10)
    async def put(self, obj_id: UUID, data: str):
        await self.redis.set(self.keybuilder(obj_id), data, expire=self.ttl)


def get_redis_cache(keybuilder: Callable[[UUID], str], ttl: int = DEFAULT_TTL):
    def inner():
        return RedisCache(redis.redis, keybuilder, ttl)

    return inner
