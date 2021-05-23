import json
from functools import lru_cache

from fastapi import Depends

from common.errors import UserNotFound, InvalidUUID
from common.utils import is_valid_uuid
from connections.redis import get_redis_db_connection
from storage.elastic import get_elastic_storage


class PersonalService:
    def __init__(self, recommendation_connection, movies_storage) -> dict:
        self.recommendation_connection = recommendation_connection
        self.movies_storage = movies_storage

    async def get_personal_recommendations(self, user_id):
        if not is_valid_uuid(user_id):
            raise InvalidUUID(user_id)

        recommendations = (
            await self.recommendation_connection.get(user_id)
        )
        if recommendations:
            recommendations_dict = dict(json.loads(recommendations))
            return recommendations_dict

        recommendations = await self.movies_storage.get_ordered_list('movies')

        if not recommendations:
            raise UserNotFound(user_id)
        return {'must_watch': recommendations}


@lru_cache()
def get_personal_service(
        storage=Depends(get_redis_db_connection),
        movies_storage=Depends(get_elastic_storage)):
    return PersonalService(storage, movies_storage)
