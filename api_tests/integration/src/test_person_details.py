import pytest


@pytest.mark.asyncio
async def test_get_existing_person(make_get_request, es_prepare_persons):
    response = await make_get_request('/person/0058afdf-12fa-4a20-8fb6-cc8460793b51')
    assert response.status == 200
    assert response.body['name'] == 'Rufus King'


@pytest.mark.asyncio
async def test_get_nonexistant_person(make_get_request, es_prepare_persons):
    response = await make_get_request('/person/11cc6e47-306a-45d9-bf15-77b3643c9cc8')
    assert response.status == 404
