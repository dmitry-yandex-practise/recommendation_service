from collections import OrderedDict
from enum import Enum
from functools import lru_cache
from typing import List, Optional, Tuple
from uuid import UUID

from fastapi import Depends

from cache.abstract import Cache
from cache.redis import RedisCache
from db import redis
from models.person import Person
from storage.abstract import Storage
from storage.elastic import get_elastic_storage

PERSONS_INDEX = 'persons'


class Roles(Enum):
    ACTOR = 'actors'
    DIRECTOR = 'directors'
    WRITER = 'writers'


def persons_keybuilder(person_id: UUID) -> str:
    return f'person:{str(person_id)}'


def _build_person_serch_query(name: str) -> List:
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


class PersonService:

    def __init__(self, cache: Cache, storage: Storage):
        self.cache = cache
        self.storage = storage
        self._index = PERSONS_INDEX

    async def list(self,
                   page_number: int,
                   page_size: int) -> Tuple[int, List[Person]]:
        """
        Возвращает все персоны
        """
        # получаем только ID персон
        params = {
            "size": page_size,
            "from": page_size * (page_number - 1),
            "sort": "id"
        }
        persons_total, person_ids = await self.storage.search(self._index, params=params)
        persons = await self.get_by_ids(person_ids)
        return (persons_total, persons)

    async def get_by_id(self, person_id: UUID) -> List[Person]:

        """
        Возвращает объект персоны. Он опционален, так как
        персона может отсутствовать в базе
        """

        data = await self.cache.get(person_id)
        if data:
            return Person.parse_raw(data)

        docs = await self.storage.get_by_ids(self._index, [person_id, ])
        if not docs:
            return None
        person = Person(**docs[0])
        await self.cache.put(person.id, person.json())
        return person

    async def get_by_ids(self, person_ids: List[UUID]) -> Optional[List[Person]]:
        """
        Возвращает персоны по списку id.
        """
        persons = OrderedDict.fromkeys(person_ids, None)

        # проверяем есть ли полученные жанры в кеше по их ID
        for person_id in persons.keys():
            data = await self.cache.get(person_id)
            if data:
                persons[person_id] = Person.parse_raw(data)

        # не найденные в кеше персоны запрашиваем в эластике и кладём в кеш
        not_found = [person_id for person_id in persons.keys()
                     if persons[person_id] is None]
        if not_found:
            docs = await self.storage.get_by_ids(self._index, not_found)
            for doc in docs:
                person = Person(**doc)
                await self.cache.put(person.id, person.json())
                persons[person.id] = person
        return list(persons.values())

    async def search(self, query: str) -> Optional[List[Person]]:
        """
        Поиск по персонам.
        """
        body = _build_person_serch_query(query)
        _, person_ids = await self.storage.search(self._index, body)
        if not person_ids:
            return None

        return await self.get_by_ids(person_ids)


@lru_cache()
def get_person_redis_cache():
    return RedisCache(redis.redis, persons_keybuilder)


@lru_cache()
def get_person_service(
        cache: Cache = Depends(get_person_redis_cache),
        storage: Storage = Depends(get_elastic_storage)

) -> PersonService:
    return PersonService(cache,
                         storage)
