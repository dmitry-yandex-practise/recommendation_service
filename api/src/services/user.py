from functools import lru_cache
from typing import Optional
from uuid import UUID

from fastapi import Depends
import requests

from cache.abstract import Cache
from cache.redis import RedisCache
from core.config import RECOMMENDATIONS_PORT, RECOMMENDATIONS_HOST
from db import redis
from models.user import User
from models.film import Film
from storage.abstract import Storage
from storage.elastic import get_elastic_storage


def user_keybuilder(user_id: UUID) -> str:
    return f'user:{str(user_id)}'


class UserService:
    def __init__(self, cache: Cache, storage: Storage):
        self.cache = cache
        self.storage = storage

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Возвращает объект пользователя. Он опционален, так как
        пользователь может отсутствовать в базе
        """
        data = await self.cache.get(user_id)
        if data:
            return User.parse_raw(data)

        must_watch = requests.get(f'http://{RECOMMENDATIONS_HOST}:{RECOMMENDATIONS_PORT}/v1/user/{user_id}')
        must_watch = must_watch.json()
        if must_watch['error']:
            return None

        must_watch = must_watch['result']

        docs = await self.storage.get_by_ids('movies', must_watch)
        if not docs:
            return None
        must_watch = [Film(**doc) for doc in docs]

        user = User(id=user_id, must_watch=must_watch)
        await self.cache.put(user.id, user.json())
        return user


@lru_cache()
def get_user_redis_cache():
    return RedisCache(redis.redis, user_keybuilder)


@lru_cache()
def get_user_service(
        cache: Cache = Depends(get_user_redis_cache),
        storage: Storage = Depends(get_elastic_storage),
) -> UserService:
    return UserService(cache,
                       storage)
