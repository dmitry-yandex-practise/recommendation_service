from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from api.v1.models import PopularMovies, PopularPersons
from services.analytic import AnalyticService, get_analytic_service

router = APIRouter()


@router.get('/movies/', response_model=PopularMovies)
async def popular_movies(
        analytic_service: AnalyticService = Depends(get_analytic_service)
) -> PopularMovies:
    film_work_ids = analytic_service.get_popular_movies()
    return PopularMovies(movies=film_work_ids)

@router.get('/persons/', response_model=PopularPersons)
async def popular_persons(
        analytic_service: AnalyticService = Depends(get_analytic_service)
) -> PopularMovies:
    person_ids = analytic_service.get_popular_persons()
    return PopularPersons(persons=person_ids)
