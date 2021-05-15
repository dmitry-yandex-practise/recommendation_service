import pytest


@pytest.mark.asyncio
async def test_person_films(make_get_request, es_prepare_movies, es_prepare_persons):
    response = await make_get_request('/person/0058afdf-12fa-4a20-8fb6-cc8460793b51/film')
    assert response.status == 200

    have = []
    for item in response.body:
        have.append(item["id"])
    expected = ['3e3117ce-de3a-48a1-9772-4243bd1c0f3a', '66d4daa4-4925-4a35-8897-afedbdbe3f8b']
    assert sorted(have) == expected


@pytest.mark.asyncio
async def test_nonexisting_person_films(make_get_request, es_prepare_movies, es_prepare_persons):
    response = await make_get_request('/person/90b6896a-e08d-4906-a0f1-42b7944f7aae/film')
    assert response.status == 404


@pytest.mark.asyncio
async def test_filter_person_films_by_role(make_get_request, es_prepare_movies, es_prepare_persons):
    response = await make_get_request('/person/0058afdf-12fa-4a20-8fb6-cc8460793b51/film', params={'role': 'actor'})
    assert response.status == 200
    assert len(response.body) == 1

    response = await make_get_request('/person/0058afdf-12fa-4a20-8fb6-cc8460793b51/film', params={'role': 'writer'})
    assert response.status == 200
    assert len(response.body) == 1
