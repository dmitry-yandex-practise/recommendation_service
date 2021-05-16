from fastapi.testclient import TestClient

from api_tests.functional.mocks.cache import get_emptycache_mock
from api_tests.functional.mocks.redis import get_mock_redis
from api_tests.functional.mocks.storage import get_mock_storage
from db import redis
from main import app
from services.genre import get_genre_redis_cache
from storage.elastic import get_elastic_storage

client = TestClient(app)

app.dependency_overrides[get_genre_redis_cache] = get_emptycache_mock
app.dependency_overrides[get_elastic_storage] = get_mock_storage

redis.redis = get_mock_redis()


def test_list_genres():
    response = client.get("/v1/genre/")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2


def test_get_genre():
    response = client.get("/v1/genre/8519222a-9a84-4a05-8a56-96f7c14d97bb/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "War"
