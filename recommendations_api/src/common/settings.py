import os
from dotenv import load_dotenv

load_dotenv()


RECOMMENDATIONS_HOST = os.getenv('RECOMMENDATIONS_HOST', '127.0.0.1')
RECOMMENDATIONS_PORT = int(os.getenv('RECOMMENDATIONS_PORT', 6379))

APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
APP_PORT = os.getenv('APP_PORT', '8000')

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))
ELASTIC_USER = os.getenv('ELASTIC_USER', 'admin')
ELASTIC_PASS = os.getenv('ELASTIC_PASS', 'zaq123321qaz')
ELASTIC_CA_PATH = os.getenv('ELASTIC_CA_PATH', '/src/CA.pem')
ELASTIC_HOSTS = os.getenv('ELASTIC_HOSTS', 'localhost').replace("M", "").split(",")

CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST', '127.0.0.1')
