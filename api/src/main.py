import logging

import aioredis
from aiokafka import AIOKafkaProducer
import uvicorn as uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import film, genre, person, event
from core import config
from core.logger import LOGGING
from db import elastic, redis, kafka
from utils import str_to_bytes

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.create_redis_pool((config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20)
    elastic.es = AsyncElasticsearch(
        hosts=config.ELASTIC_HOSTS,
        use_ssl=True,
        verify_certs=True,
        http_auth=(config.ELASTIC_USER, config.ELASTIC_PASS),
        ca_certs=config.ELASTIC_CA_PATH)
    kafka.kafka_producer = AIOKafkaProducer(
        bootstrap_servers=f'{config.BROKER_HOST}:{config.BROKER_PORT}',
        key_serializer=str_to_bytes,
        value_serializer=str_to_bytes)
    await kafka.kafka_producer.start()


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()
    await kafka.kafka_producer.stop()


app.include_router(film.router, prefix='/v1/film', tags=['film'])
app.include_router(genre.router, prefix='/v1/genre', tags=['genre'])
app.include_router(person.router, prefix='/v1/person', tags=['person'])
app.include_router(event.router, prefix='/v1/event', tags=['event'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=config.APP_HOST,
        port=int(config.APP_PORT),
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
