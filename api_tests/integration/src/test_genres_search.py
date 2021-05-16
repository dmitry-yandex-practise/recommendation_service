import pytest

from api.src.services.genre import genres_keybuilder, Genre


@pytest.mark.asyncio
async def test_genre_search(make_get_request, es_prepare_genres):
    found = None
    response = await make_get_request('/genre/search/', params={'query': 'Mystery'})
    for item in response.body:
        if item.get('id') == '0c0bdb6f-3ee8-458b-8f2b-6e1b66e7a207':
            found = item
            break
    assert response.status == 200
    assert found['id'] == '0c0bdb6f-3ee8-458b-8f2b-6e1b66e7a207'
    assert found['name'] == 'Mystery'


@pytest.mark.asyncio
async def test_genre_search_cache(make_get_request, es_prepare_genres, redis_client):
    genre_id = '0c0bdb6f-3ee8-458b-8f2b-6e1b66e7a207'
    response = await make_get_request('/genre/search/', params={'query': 'Mystery'})
    assert response.status == 200
    data = await redis_client.get(genres_keybuilder(genre_id))
    genre_from_cache = Genre.parse_raw(data)
    assert genre_from_cache.name == 'Mystery'
