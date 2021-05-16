import asyncio
from dataclasses import dataclass

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch, helpers
from multidict import CIMultiDictProxy

from api.src.services.film import FILMS_INDEX
from api.src.services.genre import GENRES_INDEX
from api.src.services.person import PERSONS_INDEX
from api_tests.integration.testdata.genres import genres
from api_tests.integration.testdata.movies import movies
from api_tests.integration.testdata.persons import persons
from api_tests.settings import test_settings

SERVICE_URL = f'http://{test_settings.app_host}:{test_settings.app_port}/'
ELASTIC_URL = f'http://{test_settings.es_host}:{test_settings.es_port}/'
REDIS_URL = f'redis://{test_settings.redis_host}:{test_settings.redis_port}/'


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def redis_client():
    conn = await aioredis.create_redis_pool(
        REDIS_URL,
        minsize=10,
        maxsize=20)
    client = aioredis.Redis(conn)
    yield client
    client.close()
    await client.wait_closed()


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=ELASTIC_URL)
    yield client
    await client.close()


@pytest.fixture(autouse=True)
async def redis_prepare(redis_client):
    # Чистим кэш до и после каждого теста
    await redis_client.flushall()
    yield redis_client
    await redis_client.flushall()


@pytest.fixture(scope='session')
async def es_prepare_persons(es_client):
    # Наполняем эластик данными
    await helpers.async_bulk(es_client, persons, index=PERSONS_INDEX, refresh="wait_for")
    yield
    # Удаляем данные из индекса в эластике
    await es_client.delete_by_query(index=PERSONS_INDEX, body={"query": {"match_all": {}}})


@pytest.fixture(scope='session')
async def es_prepare_movies(es_client):
    # Наполняем эластик данными
    await helpers.async_bulk(es_client, movies, index=FILMS_INDEX, refresh="wait_for")
    yield
    # Удаляем данные из индекса в эластике
    await es_client.delete_by_query(index=FILMS_INDEX, body={"query": {"match_all": {}}})


@pytest.fixture(scope='session')
async def es_prepare_genres(es_client):
    # Наполняем эластик данными
    await helpers.async_bulk(es_client, genres, index=GENRES_INDEX, refresh="wait_for")
    yield
    # Удаляем данные из индекса в эластике
    await es_client.delete_by_query(index=GENRES_INDEX, body={"query": {"match_all": {}}})


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
async def make_get_request(session):
    async def inner(method: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        headers = {'accept': 'application/json'}
        url = SERVICE_URL + 'v1' + method  # в боевых системах старайтесь так не делать!
        async with session.get(url, params=params, headers=headers) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner
