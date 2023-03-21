import logging
import os
from logging import config as logging_config

from pydantic import BaseSettings, Field

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    project_name: str = Field(default="movies", env="PROJECT_NAME")
    redis_host: str = Field(default="127.0.0.1", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    elastic_host: str = Field(default="127.0.0.1", env="ELASTIC_HOST")
    elastic_port: str = Field(default=9200, env="ELASTIC_PORT")
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_expire_in_seconds: int = Field(default=60, env="CACHE_EXPIRE_SEC")
    debug_log_level: bool = Field(default=False, env="DEBUG")

    class Config:
        env_file = ".env"


settings = Settings()

log_level = logging.DEBUG if settings else logging.INFO
