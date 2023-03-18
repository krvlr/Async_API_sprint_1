import os
import sys

from dotenv import load_dotenv
from loguru import logger
from redis import Redis

load_dotenv()


logger.remove()
logger.add(sys.stderr, level="DEBUG" if os.environ.get("DEBUG") == "True" else "INFO")

REDIS_ADAPTER = Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=int(os.environ.get("REDIS_PROT", "6379")),
    db=0,
    decode_responses=True,
)

ETL_BATCH_SIZE: int = int(os.environ.get("ETL_BATCH_SIZE", 100))

POSTGRES_CONNECTION_SETTINGS = {
    "host": os.environ.get("DB_HOST"),
    "port": os.environ.get("DB_PORT"),
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
}

ELASTIC_SEARCH_URL = f'http://{os.environ.get("ELASTIC_HOST", "elasticsearch")}:{os.environ.get("ELASTIC_PORT", 9200)}'


ETL_REPEAT_INTERVAL_TIME_SEC: int = int(os.environ.get("ETL_REPEAT_INTERVAL_TIME_SEC", 60))
