import pytest

from api.src.services.film import films_keybuilder, Film


@pytest.mark.asyncio
async def test_get_film_by_id(make_get_request, es_prepare_movies):
    response = await make_get_request('/film/3e3117ce-de3a-48a1-9772-4243bd1c0f3a')
    assert response.status == 200
    assert response.body['title'] == 'Star Spangled Rhythm'


@pytest.mark.asyncio
async def test_get_film_by_nonexistent_id(make_get_request, es_prepare_movies):
    response = await make_get_request('/film/3e3117ce-de3a-48a1-9772-4243bd1c0f3f')
    assert response.status == 404


@pytest.mark.asyncio
async def test_get_film_by_non_uuid(make_get_request, es_prepare_movies):
    response = await make_get_request('/film/123456789')
    assert response.status == 422


@pytest.mark.asyncio
async def test_get_film_by_id_uses_cache(make_get_request, es_prepare_movies, redis_client):
    film_id = '3e3117ce-de3a-48a1-9772-4243bd1c0f3a'
    response = await make_get_request(f'/film/{film_id}')
    assert response.status == 200
    data = await redis_client.get(films_keybuilder(film_id))
    film_from_cache = Film.parse_raw(data)
    assert film_from_cache.title == 'Star Spangled Rhythm'
