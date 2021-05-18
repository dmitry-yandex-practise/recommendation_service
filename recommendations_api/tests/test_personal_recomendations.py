import json

import requests
from aioredis import create_redis_pool

import asynctest


RECOMMENDATIONS_HOST = '127.0.0.1'
RECOMMENDATIONS_PORT = 6379


class TestPR(asynctest.TestCase):
    async def setUp(self) -> None:
        self.conn = await create_redis_pool((RECOMMENDATIONS_HOST, RECOMMENDATIONS_PORT))
        await self.conn.set('77dacbc1-eecd-422d-a68c-39021e033082', json.dumps({'must_watch':
                                                                         ['93a1b3e2-1090-497e-863c-e4d634a5c14b']}))

    async def test_pr(self):
        print(f'REDIS DATA: {await self.conn.get("77dacbc1-eecd-422d-a68c-39021e033082")}')
        result = requests.get('http://127.0.0.1:8004/v1/user/77dacbc1-eecd-422d-a68c-39021e033082')
        result = result.json()
        print(f'RESULT: {result}')
        assert result['result'] == ['93a1b3e2-1090-497e-863c-e4d634a5c14b']
        assert result['error'] is None

        result = requests.get('http://127.0.0.1:8004/v1/user/test')
        result = result.json()
        assert result['result'] is None
        assert result['error'] == 'Value "test" is not a valid UUID4'


if __name__ == '__main__':
    asynctest.main()
