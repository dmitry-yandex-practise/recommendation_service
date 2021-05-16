import pytest


@pytest.mark.asyncio
async def test_genre_list(make_get_request, es_prepare_genres):
    response = await make_get_request('/genre/')
    assert response.status == 200
    assert len(response.body['result']) == 26


@pytest.mark.asyncio
async def test_genre_first_page(make_get_request, es_prepare_genres):
    params = {'page[size]': 5, 'page[number]': 1}
    response = await make_get_request('/genre/', params=params)
    assert response.status == 200
    assert len(response.body['result']) == 5
    assert response.body['page_number'] == 1


@pytest.mark.asyncio
async def test_genre_last_page(make_get_request, es_prepare_genres):
    params = {'page[size]': 5, 'page[number]': 6}
    response = await make_get_request('/genre/', params=params)
    assert response.status == 200
    assert len(response.body['result']) == 1
    assert response.body['total_pages'] == 6


@pytest.mark.asyncio
async def test_genre_second_page(make_get_request, es_prepare_genres):
    params = {'page[size]': 5, 'page[number]': 2}
    response = await make_get_request('/genre/', params=params)
    assert response.status == 200
    assert len(response.body['result']) == 5
    assert response.body['page_number'] == 2


@pytest.mark.asyncio
async def test_genre_nonexisting_page(make_get_request, es_prepare_genres):
    params = {'page[size]': 5, 'page[number]': 7}
    response = await make_get_request('/genre/', params=params)
    assert response.status == 404


@pytest.mark.asyncio
async def test_genre_negative_page_number(make_get_request, es_prepare_genres):
    params = {'page[size]': 5, 'page[number]': -1}
    response = await make_get_request('/genre/', params=params)
    assert response.status == 422
