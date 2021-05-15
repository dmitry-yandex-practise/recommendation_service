from fastapi.testclient import TestClient

from api_tests.functional.mocks.cache import get_emptycache_mock
from api_tests.functional.mocks.redis import get_mock_redis
from api_tests.functional.mocks.storage import get_mock_storage
from db import redis
from main import app
from services.person import get_person_redis_cache
from storage.elastic import get_elastic_storage

client = TestClient(app)

app.dependency_overrides[get_person_redis_cache] = get_emptycache_mock
app.dependency_overrides[get_elastic_storage] = get_mock_storage

redis.redis = get_mock_redis()


def test_list_persons():
    response = client.get("/v1/person/")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3


def test_get_person():
    response = client.get("/v1/person/230f2183-0103-479c-858f-1cae2890f1c3/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "William Russell"
    assert len(data["actor"]) != 0


def test_search_person():
    response = client.get("/v1/person/search/", params={"query": "iddqd"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_get_person_films():
    response = client.get("/v1/person/230f2183-0103-479c-858f-1cae2890f1c3/film")
    assert response.status_code == 200
