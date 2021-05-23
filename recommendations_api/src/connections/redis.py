from uuid import UUID
from socket import gaierror

from aioredis import Redis
import backoff

from connections.basic import BasicConnection
from db import redis

exceptions_list = (gaierror,)


class RedisDbConnection(BasicConnection):
    def __init__(self, conn: Redis):
        self.conn = conn

    @backoff.on_exception(backoff.expo, exceptions_list, max_tries=10)
    def get(self, user_id: UUID):
        return self.conn.get(user_id)


def get_redis_db_connection() -> RedisDbConnection:
    return RedisDbConnection(conn=redis.redis)
