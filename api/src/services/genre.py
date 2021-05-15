from collections import OrderedDict
from functools import lru_cache
from typing import Optional, List, Tuple
from uuid import UUID

from fastapi import Depends

from cache.abstract import Cache
from cache.redis import RedisCache
from db import redis
from models.genre import Genre
from storage.abstract import Storage
from storage.elastic import get_elastic_storage

GENRES_INDEX = 'genres'


def genres_keybuilder(genre_id: UUID) -> str:
    return f'genre:{str(genre_id)}'


def _build_genre_serch_query(name: str) -> List:
    query = {
        'query': {
            'match': {
                'name': {
                    'query': name,
                    'fuzziness': 'auto'
                }
            }
        }
    }

    return query


class GenreService:
    def __init__(self, cache: Cache, storage: Storage):
        self.cache = cache
        self.storage = storage
        self._index = GENRES_INDEX

    async def get_by_id(self, genre_id: UUID) -> Optional[Genre]:
        """
        Возвращает объект жанра. Он опционален, так как
        жанр может отсутствовать в базе
        """
        data = await self.cache.get(genre_id)
        if data:
            return Genre.parse_raw(data)

        docs = await self.storage.get_by_ids(self._index, [genre_id, ])
        if not docs:
            return None
        genre = Genre(**docs[0])
        await self.cache.put(genre.id, genre.json())
        return genre

    async def list(self,
                   page_number: int,
                   page_size: int) -> Tuple[int, List[Genre]]:
        """
        Возвращает все жанры
        """
        # получаем только ID жанров
        params = {
            "size": page_size,
            "from": page_size * (page_number - 1),
            "sort": "id"
        }
        genres_total, genre_ids = await self.storage.search(self._index, params=params)
        genres = OrderedDict.fromkeys(genre_ids, None)

        # проверяем есть ли полученные жанры в кеше по их ID
        for genre_id in genres.keys():
            data = await self.cache.get(genre_id)
            if data:
                genres[genre_id] = Genre.parse_raw(data)

        # не найденные в кеше жанры запрашиваем в эластике и кладём в кеш
        not_found = [genre_id for genre_id in genres.keys()
                     if genres[genre_id] is None]
        if not_found:
            docs = await self.storage.get_by_ids(self._index, not_found)
            for doc in docs:
                genre = Genre(**doc)
                await self.cache.put(genre.id, genre.json())
                genres[genre.id] = genre
        return (genres_total, list(genres.values()))

    async def get_by_ids(self, genre_ids: List[UUID]) -> Optional[List[Genre]]:
        """
        Возвращает жанры по списку id.
        """
        genres = OrderedDict.fromkeys(genre_ids, None)

        # проверяем есть ли полученные жанры в кеше по их ID
        for genre_id in genres.keys():
            data = await self.cache.get(genre_id)
            if data:
                genres[genre_id] = Genre.parse_raw(data)

        # не найденные в кеше жанры запрашиваем в эластике и кладём в кеш
        not_found = [genre_id for genre_id in genres.keys()
                     if genres[genre_id] is None]
        if not_found:
            docs = await self.storage.get_by_ids(self._index, not_found)
            for doc in docs:
                genre = Genre(**doc)
                await self.cache.put(genre.id, genre.json())
                genres[genre.id] = genre
        return list(genres.values())

    async def search(self, query: str) -> Optional[List[Genre]]:
        """
        Поиск по жанрам.
        """
        body = _build_genre_serch_query(query)
        _, genre_ids = await self.storage.search(self._index, body)
        if not genre_ids:
            return None

        return await self.get_by_ids(genre_ids)


@lru_cache()
def get_genre_redis_cache():
    return RedisCache(redis.redis, genres_keybuilder)


@lru_cache()
def get_genre_service(
        cache: Cache = Depends(get_genre_redis_cache),
        storage: Storage = Depends(get_elastic_storage),
) -> GenreService:
    return GenreService(cache,
                        storage)
