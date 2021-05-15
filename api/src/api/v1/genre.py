from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status

from api.v1.common import pagination
from api.v1.models import Genre, PaginatedGenreList, GenreList
from cache.redis import cache_response
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get('/{genre_id}', response_model=Genre)
@cache_response(ttl=60 * 5, query_args=['genre_id'])
async def genre_details(
        genre_id: UUID,
        genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    """
    Детальная информация о жанре
    """

    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='genre not found')
    return Genre.from_model(genre)


@router.get('/search/', response_model=GenreList)
@cache_response(ttl=60 * 5, query_args=['query'])
async def genres_search(
        request: Request,
        query: str,
        genre_service: GenreService = Depends(get_genre_service)
) -> List[Genre]:
    """
    Поиск по персонам
    """

    genres = await genre_service.search(query)
    if not genres:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='genres not found')

    return GenreList(__root__=[Genre.from_model(genre) for genre in genres])


@router.get('/', response_model=PaginatedGenreList)
@cache_response(ttl=60 * 5, query_args=['sort'])
async def genres(
        request: Request,
        genre_service: GenreService = Depends(get_genre_service),
        pagination: dict = Depends(pagination)
) -> List[Genre]:
    """
    Список жанров
    """

    page_number = pagination['pagenumber']
    page_size = pagination['pagesize']

    genres_total, genres = await genre_service.list(page_number, page_size)
    if not genres:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='genres not found')

    response = PaginatedGenreList(
        page_number=page_number,
        count=len(genres),
        total_pages=(genres_total // page_size) + 1,
        result=[Genre.from_model(genre) for genre in genres],
    )
    return response
