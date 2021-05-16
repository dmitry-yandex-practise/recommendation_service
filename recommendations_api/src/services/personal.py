import json
from functools import lru_cache

from fastapi import Depends

from common.errors import UserNotFound, InvalidUUID
from common.utils import is_valid_uuid
from db.redis import get_redis


class PersonalService:
    def __init__(self, storage):
        self.storage = storage

    async def get_personal_recommendations(self, user_id):
        if not is_valid_uuid(user_id):
            raise InvalidUUID(user_id)

        recommendations = (
            await self.storage.get(user_id)
        )
        if not recommendations:
            raise UserNotFound(user_id)

        recommendations_dict = dict(json.loads(recommendations))
        return list(recommendations_dict['must_watch'])


@lru_cache()
def get_personal_service(
        storage=Depends(get_redis)):
    return PersonalService(storage)
