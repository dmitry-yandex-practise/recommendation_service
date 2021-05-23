from uuid import UUID

from aioredis import Redis

from connections.basic import BasicConnection
from db import redis


class RedisDbConnection(BasicConnection):
    def __init__(self, conn: Redis):
        self.conn = conn

    def get(self, user_id: UUID):
        return self.conn.get(user_id)


def get_redis_db_connection() -> RedisDbConnection:
    return RedisDbConnection(conn=redis.redis)
