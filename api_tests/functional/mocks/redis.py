class MockRedis:
    async def get(*args, **kwargs):
        return None

    async def set(*args, **kwargs):
        pass


def get_mock_redis():
    return MockRedis()
