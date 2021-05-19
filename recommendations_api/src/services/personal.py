import json
from functools import lru_cache

from fastapi import Depends

from common.errors import UserNotFound, InvalidUUID
from common.utils import is_valid_uuid
from db.redis import get_redis
from storage.elastic import get_elastic_storage


class PersonalService:
    def __init__(self, storage, movies_storage):
        self.storage = storage
        self.movies_storage = movies_storage

    async def get_personal_recommendations(self, user_id):
        if not is_valid_uuid(user_id):
            raise InvalidUUID(user_id)

        recommendations = (
            await self.storage.get(user_id)
        )
        if recommendations:
            recommendations_dict = dict(json.loads(recommendations))
            return list(recommendations_dict['must_watch'])

        try:
            recommendations = await self.movies_storage.get_ordered_list('movies')
        except:
            raise UserNotFound(user_id)
        if not recommendations:
            raise UserNotFound(user_id)
        return recommendations


@lru_cache()
def get_personal_service(
        storage=Depends(get_redis),
        movies_storage=Depends(get_elastic_storage)):
    return PersonalService(storage, movies_storage)
