import pytest

from api.src.services.film import films_keybuilder, Film


@pytest.mark.asyncio
async def test_get_all(make_get_request, es_prepare_movies):
    response = await make_get_request('/film/')
    assert response.status == 200
    assert len(response.body['result']) == 6


@pytest.mark.asyncio
async def test_pagination(make_get_request, es_prepare_movies):
    params = {'page[size]': 5, 'page[number]': 1}
    response = await make_get_request('/film/', params=params)
    assert response.status == 200
    assert len(response.body['result']) == response.body['count']
    assert response.body['page_number'] == 1
    assert response.body['total_pages'] == 2


@pytest.mark.asyncio
async def test_pagination_nonexistent_page(make_get_request, es_prepare_movies):
    params = {'page[size]': 5, 'page[number]': 4}
    response = await make_get_request('/film/', params=params)
    assert response.status == 404


@pytest.mark.asyncio
async def test_filter_by_genre(make_get_request, es_prepare_movies):
    params = {'filter[genre]': '0c4a2110-db3c-4778-8034-c4d96a125b5e'}
    response = await make_get_request('/film/', params=params)
    assert response.status == 200
    assert len(response.body['result']) == 2


@pytest.mark.asyncio
async def test_filter_by_nonexistent_genre(make_get_request, es_prepare_movies):
    params = {'filter[genre]': '0c4a2110-db3c-4778-8034-c4d96a125b5f'}
    response = await make_get_request('/film/', params=params)
    assert response.status == 404


@pytest.mark.asyncio
async def test_filter_by_actor(make_get_request, es_prepare_movies):
    params = {'filter[actor]': '0e7be8fd-9491-4f0d-8944-133b91af6898'}
    response = await make_get_request('/film/', params=params)
    assert response.status == 200
    assert len(response.body['result']) == 1


@pytest.mark.asyncio
async def test_filter_by_nonexistent_actor(make_get_request, es_prepare_movies):
    params = {'filter[actor]': '0e7be8fd-9491-4f0d-8944-133b91af6899'}
    response = await make_get_request('/film/', params=params)
    assert response.status == 404


@pytest.mark.asyncio
async def test_filter_by_nonexistent_attribute(make_get_request, es_prepare_movies):
    params = {'filter[producer]': '0e7be8fd-9491-4f0d-8944-133b91af6899'}
    response = await make_get_request('/film/', params=params)
    assert response.status == 404


@pytest.mark.asyncio
async def test_sort_by_rating_asc(make_get_request, es_prepare_movies):
    params = {'sort': '+imdb_rating'}
    response = await make_get_request('/film/', params=params)
    assert response.status == 200
    assert response.body['result'][0]['id'] == 'f46d1fd4-9be8-4d21-b191-4de6efcf3d97'


@pytest.mark.asyncio
async def test_sort_by_rating_desc(make_get_request, es_prepare_movies):
    params = {'sort': '-imdb_rating'}
    response = await make_get_request('/film/', params=params)
    assert response.status == 200
    assert response.body['result'][0]['id'] == '3e3117ce-de3a-48a1-9772-4243bd1c0f3a'


@pytest.mark.asyncio
async def test_missing_sort_order(make_get_request, es_prepare_movies):
    params = {'sort': 'imdb_rating'}
    response = await make_get_request('/film/', params=params)
    assert response.status == 422


@pytest.mark.asyncio
async def test_wrong_sort_attribute(make_get_request, es_prepare_movies):
    params = {'sort': '+actors'}
    response = await make_get_request('/film/', params=params)
    assert response.status == 200
    # результат — сортировка по рейтингу в порядке убывания (как в test_sort_by_rating_desc)
    assert response.body['result'][0]['id'] == '3e3117ce-de3a-48a1-9772-4243bd1c0f3a'


@pytest.mark.asyncio
async def test_get_all_uses_cache(make_get_request, es_prepare_movies, redis_client):
    response = await make_get_request('/film/')
    assert response.status == 200
    film_id = '3e3117ce-de3a-48a1-9772-4243bd1c0f3a'
    data = await redis_client.get(films_keybuilder(film_id))
    film_from_cache = Film.parse_raw(data)
    assert film_from_cache.title == 'Star Spangled Rhythm'
