import pytest


@pytest.mark.asyncio
async def test_get_existing_genre(make_get_request, es_prepare_genres):
    response = await make_get_request('/genre/0c0bdb6f-3ee8-458b-8f2b-6e1b66e7a207')
    assert response.status == 200
    assert response.body['name'] == 'Mystery'


@pytest.mark.asyncio
async def test_get_nonexistant_genre(make_get_request, es_prepare_genres):
    response = await make_get_request('/genre/11cc6e47-306a-45d9-bf15-77b3643c9cc8')
    assert response.status == 404
