from aioredis import Redis


class RedisService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> str:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expire: int):
        await self.redis.set(key, value, expire=expire)
