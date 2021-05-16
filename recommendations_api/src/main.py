from fastapi import FastAPI
import aioredis
import uvicorn

from db import redis
from common import settings
from api.v1 import personal


app = FastAPI()


@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.create_redis_pool((settings.RECOMMENDATIONS_HOST, settings.RECOMMENDATIONS_PORT))


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()


app.include_router(personal.router, prefix='/v1/user', tags=['personal'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.APP_HOST,
        port=int(settings.APP_PORT)
    )