import json
from functools import lru_cache
from socket import gaierror
import logging

from fastapi import Depends
import backoff
from elasticsearch.exceptions import ConnectionError, ConnectionTimeout

from common.errors import InvalidUUID
from common.utils import is_valid_uuid
from connections.redis import get_redis_db_connection
from storage.elastic import get_elastic_storage


exceptions_list = (ConnectionError, ConnectionTimeout,)

logger = logging.getLogger(__name__)


class PersonalService:
    def __init__(self, recommendation_connection, movies_storage):
        self.recommendation_connection = recommendation_connection
        self.movies_storage = movies_storage

    @backoff.on_exception(backoff.expo, exceptions_list, max_tries=10, logger=logger)
    async def get_personal_recommendations(self, user_id) -> dict:
        if not is_valid_uuid(user_id):
            raise InvalidUUID(user_id)

        try:
            recommendations = (
                await self.recommendation_connection.get(user_id)
            )
            if recommendations:
                recommendations_dict = dict(json.loads(recommendations))
                return recommendations_dict
        except gaierror:
            logger.warning(f'RECOMMENDATION SYSTEM IS NOT AVAILABLE')
            pass

        recommendations = await self.movies_storage.get_ordered_list('movies')

        return {'must_watch': recommendations}


@lru_cache()
def get_personal_service(
        storage=Depends(get_redis_db_connection),
        movies_storage=Depends(get_elastic_storage)):
    return PersonalService(storage, movies_storage)
