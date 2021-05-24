from typing import List
from uuid import UUID

from pydantic import BaseModel

"""
Здесь находятся модели, которые сериализются в ответ API
"""

class PopularMovies(BaseModel):
    movies: List[UUID]

class PopularPersons(BaseModel):
    persons: List[UUID]
