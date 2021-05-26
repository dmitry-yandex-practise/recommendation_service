from typing import Optional

from redis import Redis


class RedisService:
    def __init__(self, host, port=6379):
        self.redis = Redis(host=host, port=port)

    def get(self, key: str) -> str:
        return self.redis.get(key)

    def set(self, key: str, value: str, expire: Optional[int] = None):
        self.redis.set(key, value, ex=expire)

    def ping(self):
        return self.redis.ping()
