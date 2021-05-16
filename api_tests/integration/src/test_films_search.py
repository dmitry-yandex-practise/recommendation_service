import pytest

from api.src.services.film import films_keybuilder, Film


@pytest.mark.asyncio
async def test_search_film(make_get_request, es_prepare_movies):
    found = None
    response = await make_get_request('/film/search/', params={'query': 'A security guard at Paramount'})
    for item in response.body:
        if item.get('id') == '3e3117ce-de3a-48a1-9772-4243bd1c0f3a':
            found = item
            break
    assert response.status == 200
    assert found is not None


@pytest.mark.asyncio
async def test_search_film_uses_cache(make_get_request, es_prepare_movies, redis_client):
    film_id = '3e3117ce-de3a-48a1-9772-4243bd1c0f3a'
    response = await make_get_request('/film/search/', params={'query': 'A security guard at Paramount'})
    assert response.status == 200
    data = await redis_client.get(films_keybuilder(film_id))
    film_from_cache = Film.parse_raw(data)
    assert film_from_cache.title == 'Star Spangled Rhythm'
