import pytest

from api.src.services.person import persons_keybuilder, Person


@pytest.mark.asyncio
async def test_person_search(make_get_request, es_prepare_persons):
    found = None
    response = await make_get_request('/person/search/', params={'query': 'Yumi Hara'})
    for item in response.body:
        if item.get('id') == '007d0a97-3849-44b5-bac0-211cf8066199':
            found = item
            break
    assert response.status == 200
    assert found['id'] == '007d0a97-3849-44b5-bac0-211cf8066199'
    assert found['name'] == 'Yumi Hara'


@pytest.mark.asyncio
async def test_person_search_cache(make_get_request, es_prepare_persons, redis_client):
    person_id = '007d0a97-3849-44b5-bac0-211cf8066199'
    response = await make_get_request('/person/search/', params={'query': 'Yumi Hara'})
    assert response.status == 200
    data = await redis_client.get(persons_keybuilder(person_id))
    person_from_cache = Person.parse_raw(data)
    assert person_from_cache.name == 'Yumi Hara'
