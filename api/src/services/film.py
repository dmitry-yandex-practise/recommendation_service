import re
from collections import OrderedDict
from enum import Enum
from functools import lru_cache
from typing import Optional, List, Dict, Tuple
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel
from starlette.datastructures import QueryParams

from cache.abstract import Cache
from cache.redis import RedisCache
from db import redis
from models.film import Film
from storage.abstract import Storage
from storage.elastic import get_elastic_storage

DEFAULT_LIST_SIZE = 1000
FILMS_INDEX = 'movies'


class Roles(Enum):
    ACTOR = 'actors'
    DIRECTOR = 'directors'
    WRITER = 'writers'


SORT_FIELDS = ['imdb_rating', ]

SEARCH_FIELDS = ['title', 'description',
                 'directors_names', 'actors_names', 'writers_names']


class SortOrder(Enum):
    ASC = 'asc'
    DESC = 'desc'


class FilterByAttr(Enum):
    GENRE = 'genre'
    ACTOR = 'actor'
    DIRECTOR = 'director'
    WRITER = 'writer'


FILTERBY_PATHS = {
    FilterByAttr.GENRE.value: 'genres',
    FilterByAttr.ACTOR.value: 'actors',
    FilterByAttr.DIRECTOR.value: 'directors',
    FilterByAttr.WRITER.value: 'writers',
}


class SortBy(BaseModel):
    attr: str
    order: SortOrder

    @classmethod
    def from_query(cls, param: Optional[str]):
        """
        Парсит параметр, переданный в query и возвращает SortBy.
        По-умолчанию сортирует по рейтингу в порядке убывания.
        """
        if param is None:
            return cls.construct(attr='imdb_rating', order=SortOrder.DESC)
        order = SortOrder.DESC
        if param.startswith('+'):
            order = SortOrder.ASC
        sort_field = param[1:]
        if sort_field not in SORT_FIELDS:
            return cls.construct(attr='imdb_rating', order=SortOrder.DESC)
        return cls.construct(attr=param[1:], order=order)


class FilterBy(BaseModel):
    attr: FilterByAttr
    value: str

    @classmethod
    def from_query_params(cls, query: QueryParams):
        """
        Парсит набор query параметров и возвращает FilterBy либо None.
        """
        for k, v in query.items():
            if k.startswith('filter'):
                match = re.match(r'filter\[(.+)\]', k)
                if match:
                    return cls.construct(attr=match[1], value=v)
        return None


def films_keybuilder(film_id: UUID) -> str:
    return f'film:{str(film_id)}'


def _build_filter_query(filter_by: FilterBy) -> Dict:
    """
    Формирует поисковый запрос для фильтрации по аттрибутам фильма
    """
    path = FILTERBY_PATHS.get(filter_by.attr, 'actors')
    return {
        'query': {
            'nested': {
                'path': path,
                'query': {
                    'match': {f'{path}.id': filter_by.value}
                }
            }
        }
    }


def _build_person_role_query(person_id: UUID) -> List:
    result = []
    for role in Roles:
        result.append({})
        result.append(
            {
                'query': {
                    'nested': {
                        'path': role.value,
                        'query': {
                            'match': {f'{role.value}.id': person_id}
                        }
                    }
                }
            })

    return result


def _build_film_serch_query(query: str) -> List:
    query = {
        'query': {
            'multi_match': {
                'query': query,
                'fields': SEARCH_FIELDS
            }
        }
    }

    return query


class FilmService:

    def __init__(self, cache: Cache, storage: Storage):
        self.cache = cache
        self.storage = storage
        self._index = FILMS_INDEX

    async def get_by_id(self, film_id: UUID) -> Optional[Film]:
        """
        Возвращает объект фильма. Он опционален, так как
        фильм может отсутствовать в базе
        """
        data = await self.cache.get(film_id)
        if data:
            return Film.parse_raw(data)

        docs = await self.storage.get_by_ids(self._index, [film_id, ])
        if not docs:
            return None
        film = Film(**docs[0])
        await self.cache.put(film.id, film.json())

        return film

    async def list(self,
                   page_number: int,
                   page_size: int,
                   sort_by: Optional[SortBy] = None,
                   filter_by: Optional[FilterBy] = None, ) -> Tuple[int, List[Film]]:
        """
        Возвращает общее количество фильмов и список фильмов с учётом сортировки и фильтрации.
        """
        # получаем только ID фильмов
        params = {
            'size': page_size,
            'from': page_size * (page_number - 1)
        }
        if sort_by:
            params.update({'sort': f'{sort_by.attr}:{sort_by.order.value}'})
        body = None
        if filter_by:
            body = _build_filter_query(filter_by)
        films_total, film_ids = await self.storage.search(self._index, body, params)

        films = await self.get_by_ids(film_ids)
        return (films_total, films)

    async def get_by_person_id(self, person_id: UUID) -> Dict[Roles, List[Film]]:
        """
        Возвращает фильмы в которых участвовала персона
        в разрезе по ролям
        """
        body = _build_person_role_query(person_id)
        actor, director, writer = await self.storage.msearch(self._index, body=body)
        film_ids_by_role = {
            'actor': actor,
            'director': director,
            'writer': writer,
        }
        films_by_role = {}
        for role, film_ids in film_ids_by_role.items():
            films = await self.get_by_ids(film_ids)
            # кладем список фильмов в результирующую структуру
            films_by_role[role] = films

        return films_by_role

    async def get_by_ids(self, film_ids: List[UUID]) -> Optional[List[Film]]:
        """
        Возвращает фильмы по списку id.
        """
        films = OrderedDict.fromkeys(film_ids, None)

        # проверяем есть ли полученные жанры в кеше по их ID
        for film_id in films.keys():
            data = await self.cache.get(film_id)
            if data:
                films[film_id] = Film.parse_raw(data)

        # не найденные в кеше персоны запрашиваем в эластике и кладём в кеш
        not_found = [film_id for film_id in films.keys()
                     if films[film_id] is None]
        if not_found:
            docs = await self.storage.get_by_ids(self._index, not_found)
            for doc in docs:
                film = Film(**doc)
                await self.cache.put(film.id, film.json())
                films[film.id] = film
        return list(films.values())

    async def search(self, query: str) -> Optional[List[Film]]:
        """
        Поиск по фильмам.
        """
        body = _build_film_serch_query(query)
        _, person_ids = await self.storage.search(self._index, body)
        if not person_ids:
            return None

        return await self.get_by_ids(person_ids)


@lru_cache()
def get_film_redis_cache():
    return RedisCache(redis.redis, films_keybuilder)


@lru_cache()
def get_film_service(
        cache: Cache = Depends(get_film_redis_cache),
        storage: Storage = Depends(get_elastic_storage),
) -> FilmService:
    return FilmService(cache,
                       storage)
