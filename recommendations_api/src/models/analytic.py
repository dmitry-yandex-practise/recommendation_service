from typing import List
from uuid import UUID

from pydantic import BaseModel


class Movie(BaseModel):
    film_work_id: UUID

class PopularMovies(BaseModel):
    movies: List[Movie]

class PopularUUIDS(BaseModel):
    movies: List[UUID]
