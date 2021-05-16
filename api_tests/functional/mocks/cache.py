from typing import Optional
from uuid import UUID

from cache.abstract import Cache


class MockEmptyCache(Cache):

    async def get(self, obj_id: UUID) -> Optional[str]:
        return None

    async def put(self, obj_id: UUID, data: str):
        pass


def get_emptycache_mock():
    return MockEmptyCache()
