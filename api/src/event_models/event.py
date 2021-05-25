from pydantic import BaseModel
from uuid import UUID


class BaseEvent(BaseModel):
    topic: str
    key: str
    value: str


class ReviewEvent(BaseModel):
    topic: str
    movie_id: UUID
    user_id: UUID
    score: int


class PersonViewEvent(BaseModel):
    topic: str
    person_id: UUID
    user_id: UUID


class FilmViewEvent(BaseModel):
    topic: str
    movie_id: UUID
    user_id: UUID
