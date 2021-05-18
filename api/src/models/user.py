from typing import List
from uuid import UUID

import orjson
from pydantic import BaseModel

from models.film import Film


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class User(BaseModel):
    id: UUID
    must_watch: List[Film]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
