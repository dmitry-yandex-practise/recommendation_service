import os
from logging import config as logging_config

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies-api')

# Настройки Redis
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))
ELASTIC_USER = os.getenv('ELASTIC_USER', 'admin')
ELASTIC_PASS = os.getenv('ELASTIC_PASS', 'zaq123321qaz')
ELASTIC_CA_PATH = os.getenv('ELASTIC_CA_PATH', '/src/CA.pem')
ELASTIC_HOSTS = os.getenv('ELASTIC_HOSTS', 'localhost').replace("M", "").split(",")

# Настройки приложения
APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
APP_PORT = os.getenv('APP_PORT', '8888')

# Настройки Kafka
BROKER_HOST = os.getenv('BROKER_HOST', '127.0.0.1')
BROKER_PORT = os.getenv('BROKER_PORT', 29092)

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Рекоммендательная система
RECOMMENDATIONS_HOST = os.getenv('RECOMMENDATIONS_HOST', '127.0.0.1')
RECOMMENDATIONS_PORT = os.getenv('RECOMMENDATIONS_PORT', '8000')
