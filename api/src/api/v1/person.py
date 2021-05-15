from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi import status

from api.v1.common import pagination
from api.v1.models import PersonList, Person, PaginatedPersonShortList, PersonShort, FilmShortList, FilmShort
from cache.redis import cache_response
from services.film import FilmService, get_film_service
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get('/{person_id}', response_model=Person)
# @cache_response(ttl=60 * 5, query_args=['person_id'])
async def person_details(
        person_id: UUID,
        person_service: PersonService = Depends(get_person_service),
        film_service: FilmService = Depends(get_film_service)
) -> Person:
    """
    Детальная информация о персоне
    """

    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='person not found')
    person_films = await film_service.get_by_person_id(person.id)

    return Person.from_model(person, person_films)


@router.get('/{person_id}/film', response_model=FilmShortList)
@cache_response(ttl=60 * 5, query_args=['person_id'])
async def person_films(
        person_id: UUID,
        person_service: PersonService = Depends(get_person_service),
        film_service: FilmService = Depends(get_film_service),
        role: Optional[str] = Query(None, description="Фильтрация по роли персоны в фильме"),
) -> FilmShortList:
    """
    Фильмы, в которых участвовала персона
    """

    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='person not found')
    person_films_by_role = await film_service.get_by_person_id(person.id)
    person_films = []
    if role is None:
        for films in person_films_by_role.values():
            person_films.extend(films)
    else:
        person_films.extend(person_films_by_role.get(role, []))

    return FilmShortList(
        __root__=[FilmShort.from_model(film) for film in person_films]
    )


@router.get('/search/', response_model=PersonList)
@cache_response(ttl=60 * 5, query_args=['query'])
async def persons_search(
        request: Request,
        query: str,
        person_service: PersonService = Depends(get_person_service),
        film_service: FilmService = Depends(get_film_service)
) -> List[Person]:
    """
    Поиск по персонам
    """

    persons = await person_service.search(query)
    if not persons:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='persons not found')

    response_person_models = []
    for person in persons:
        person_films = await film_service.get_by_person_id(person.id)
        response_person_models.append(Person.from_model(person, person_films))

    return PersonList(__root__=response_person_models)


@router.get('/', response_model=PaginatedPersonShortList)
@cache_response(ttl=60 * 5, query_args=['sort'])
async def persons(
        request: Request,
        person_service: PersonService = Depends(get_person_service),
        pagination: dict = Depends(pagination)
) -> List[Person]:
    """
    Список персон
    """

    page_number = pagination['pagenumber']
    page_size = pagination['pagesize']

    persons_total, persons = await person_service.list(page_number, page_size)
    if not persons:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='persons not found')

    return PaginatedPersonShortList(
        page_number=page_number,
        count=len(persons),
        total_pages=(persons_total // page_size) + 1,
        result=[PersonShort.from_model(person) for person in persons]
    )
