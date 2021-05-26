from dataclasses import dataclass
from os import getenv


@dataclass
class Config:
    # Postgres connection values
    PG_HOST: str = getenv('PG_HOST', "localhost")
    PG_DATABASE: str = getenv('PG_DATABASE', "movies_database")
    PG_USER: str = getenv('PG_USER', "postgres")
    PG_PASSWORD: str = getenv('PG_PASSWORD', "pass")
    # Redis connection values
    REDIS_HOST: str = getenv('REDIS_HOST', "localhost")
    # Telegram notifications credentials
    TELEGRAM_BOT_TOKEN: str = getenv('TELEGRAM_BOT_TOKEN', "TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT: str = getenv('TELEGRAM_CHAT', "TELEGRAM_CHAT")
    # Currently user features are disabled
    USER_FEATURES: bool = False
    # default number of recommendations
    K = 10
    # percentage of data used for testing
    TEST_PERCENTAGE = 0.25
    # model learning rate
    LEARNING_RATE = 0.20
    # no of latent factors
    NO_COMPONENTS = 20
    # no of epochs to fit model
    NO_EPOCHS = 20
    # no of threads to fit model
    NO_THREADS = 8
    # regularisation for both user and item features
    ITEM_ALPHA = 1e-6
    USER_ALPHA = 1e-6
    # seed for pseudonumber generations
    SEEDNO = 42
