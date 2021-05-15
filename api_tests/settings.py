from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    es_host: str = Field('localhost', env='ELASTIC_HOST')
    es_port: int = Field(9201, env='ELASTIC_PORT')
    redis_host: str = Field('localhost', env='REDIS_HOST')
    redis_port: int = Field(6380, env='REDIS_PORT')
    app_host: str = Field('localhost', env='APP_HOST')
    app_port: int = Field(8889, env='APP_PORT')


test_settings = TestSettings()
