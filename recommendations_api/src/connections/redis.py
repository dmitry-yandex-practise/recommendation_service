from uuid import UUID
from socket import gaierror
import logging

from aioredis import Redis
import backoff

from connections.basic import BasicConnection
from db import redis

exceptions_list = (gaierror,)

logger = logging.getLogger(__name__)


class RedisDbConnection(BasicConnection):
    def __init__(self, conn: Redis):
        self.conn = conn

    @backoff.on_exception(backoff.expo, exceptions_list, max_tries=10, logger=logger)
    def get(self, user_id: UUID):
        data = self.conn.get(user_id)
        logger.info(f'RECEIVED DATA FROM REDIS: {data}')
        return data


def get_redis_db_connection() -> RedisDbConnection:
    return RedisDbConnection(conn=redis.redis)
