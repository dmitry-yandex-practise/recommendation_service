import logging

from fastapi import FastAPI
import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch

from db import redis, elastic
from common import settings
from api.v1 import personal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI()


@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.create_redis_pool((settings.RECOMMENDATIONS_HOST, settings.RECOMMENDATIONS_PORT))
    logger.info(f'CONNECTED TO REDIS SERVER {settings.RECOMMENDATIONS_HOST}:{settings.RECOMMENDATIONS_PORT}')

    elastic.es = AsyncElasticsearch(
        hosts=settings.ELASTIC_HOSTS,
        use_ssl=True,
        verify_certs=True,
        http_auth=(settings.ELASTIC_USER, settings.ELASTIC_PASS),
        ca_certs=settings.ELASTIC_CA_PATH)

    logger.info(f'CONNECTED TO ELASTICSEARCH SERVER {settings.ELASTIC_HOSTS}')


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


app.include_router(personal.router, prefix='/v1/user', tags=['personal'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.APP_HOST,
        port=int(settings.APP_PORT)
    )