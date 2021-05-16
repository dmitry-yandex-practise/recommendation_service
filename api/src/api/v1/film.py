from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi import status

from api.v1.common import pagination
from api.v1.models import FilmShort, Film, PaginatedFilmShortList, FilmShortList
from cache.redis import cache_response
from services.film import FilmService, get_film_service, SortBy, FilterBy

router = APIRouter()


@router.get('/{film_id}', response_model=Film)
@cache_response(ttl=60 * 5, query_args=['film_id'])
async def film_details(
        film_id: UUID,
        film_service: FilmService = Depends(get_film_service)
) -> Film:
    """
    Детальная информация о фильме
    """

    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='film not found')
    return Film.from_model(film)


@router.get('/', response_model=PaginatedFilmShortList)
@cache_response(ttl=60 * 5, query_args=['sort'])
async def films(
        request: Request,
        film_service: FilmService = Depends(get_film_service),
        sort: Optional[str] = Query(None,
                                    description='Сортировка по аттрибуту фильма',
                                    regex='^[-+].+$'),
        pagination: dict = Depends(pagination)
) -> List[FilmShort]:
    """
    Список фильмов.

    Кроме указанных параметров также доступна фильтрация:
    - filter[genre]=<genre_id>: фильтровать фильмы по жанру
    - filter[actor]=<actor_id>: фильтровать фильмы по актёру
    - filter[director]=<director_id>: фильтровать фильмы по режиссёру
    - filter[writer]=<writer_id>: фильтровать фильмы по сценаристуы
    """

    sort_by = SortBy.from_query(sort)
    filter_by = FilterBy.from_query_params(request.query_params)
    page_number = pagination['pagenumber']
    page_size = pagination['pagesize']

    films_total, films = await film_service.list(page_number, page_size, sort_by, filter_by)
    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='films not found')

    response = PaginatedFilmShortList(
        page_number=page_number,
        count=len(films),
        total_pages=(films_total // page_size) + 1,
        result=[FilmShort.from_model(film) for film in films],
    )
    return response


@router.get('/search/', response_model=FilmShortList)
@cache_response(ttl=60 * 5, query_args=['query'])
async def films_search(
        request: Request,
        query: str,
        film_service: FilmService = Depends(get_film_service)
) -> List[FilmShort]:
    """
    Поиск по фильмам
    """

    films = await film_service.search(query)
    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='films not found')

    return FilmShortList(
        __root__=[FilmShort.from_model(film) for film in films],
    )
