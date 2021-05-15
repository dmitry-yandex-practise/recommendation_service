import pytest


@pytest.mark.asyncio
async def test_person_list(make_get_request, es_prepare_persons):
    response = await make_get_request('/person/')
    assert response.status == 200
    assert len(response.body['result']) == 11


@pytest.mark.asyncio
async def test_person_first_page(make_get_request, es_prepare_persons):
    params = {'page[size]': 5, 'page[number]': 1}
    response = await make_get_request('/person/', params=params)
    assert response.status == 200
    assert len(response.body['result']) == 5
    assert response.body['page_number'] == 1


@pytest.mark.asyncio
async def test_person_last_page(make_get_request, es_prepare_persons):
    params = {'page[size]': 5, 'page[number]': 3}
    response = await make_get_request('/person/', params=params)
    assert response.status == 200
    assert len(response.body['result']) == 1
    assert response.body['total_pages'] == 3


@pytest.mark.asyncio
async def test_person_second_page(make_get_request, es_prepare_persons):
    params = {'page[size]': 5, 'page[number]': 2}
    response = await make_get_request('/person/', params=params)
    assert response.status == 200
    assert len(response.body['result']) == 5
    assert response.body['page_number'] == 2


@pytest.mark.asyncio
async def test_person_nonexisting_page(make_get_request, es_prepare_persons):
    params = {'page[size]': 5, 'page[number]': 4}
    response = await make_get_request('/person/', params=params)
    assert response.status == 404


@pytest.mark.asyncio
async def test_person_negative_page_number(make_get_request, es_prepare_persons):
    params = {'page[size]': 5, 'page[number]': -1}
    response = await make_get_request('/person/', params=params)
    assert response.status == 422
