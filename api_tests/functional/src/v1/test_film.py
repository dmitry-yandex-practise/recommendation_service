from fastapi.testclient import TestClient

from api_tests.functional.mocks.cache import get_emptycache_mock
from api_tests.functional.mocks.redis import get_mock_redis
from api_tests.functional.mocks.storage import get_mock_storage
from db import redis
from main import app
from services.film import get_film_redis_cache
from storage.elastic import get_elastic_storage

client = TestClient(app)

app.dependency_overrides[get_film_redis_cache] = get_emptycache_mock
app.dependency_overrides[get_elastic_storage] = get_mock_storage

redis.redis = get_mock_redis()


def test_list_films():
    response = client.get("/v1/film/")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3


def test_get_film():
    response = client.get("/v1/film/a69408b7-fcd2-45aa-92eb-5cc50778c7d6/")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "The Star of Bethlehem"


def test_search_film():
    response = client.get("/v1/film/search/", params={"query": "iddqd"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
