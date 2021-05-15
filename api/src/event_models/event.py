from pydantic import BaseModel
from uuid import UUID


class BaseEvent(BaseModel):
    topic: str
    key: str
    value: str


class ReviewEvent(BaseModel):
    topic: str
    key: UUID
    movie_id: UUID
    user_id: UUID
    score: int
