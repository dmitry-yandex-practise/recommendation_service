import os
from dotenv import load_dotenv

load_dotenv()


RECOMMENDATIONS_HOST = os.getenv('RECOMMENDATIONS_HOST', '127.0.0.1')
RECOMMENDATIONS_PORT = int(os.getenv('RECOMMENDATIONS_PORT', 6379))

APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
APP_PORT = os.getenv('APP_PORT', '8000')
