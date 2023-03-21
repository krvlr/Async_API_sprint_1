"""Функции и классы для работы с базой PostgreSQL."""

import logging.config
from contextlib import contextmanager
from typing import Generator

from config.logging import LOGGER_CONFIG
from elasticsearch import Elasticsearch
from elasticsearch import Elasticsearch as _connection
from elasticsearch import helpers

from .utils import backoff

logging.config.dictConfig(LOGGER_CONFIG)
logger = logging.getLogger(__name__)


@contextmanager
def get_conn_elastic(url: str) -> _connection:
    """
    Функция для получения
    коннекта к Elasticsearch.
    """
    logger.info('Try connecting to the Elasticsearch')
    conn = Elasticsearch(url)
    logger.info('Connection to the Elasticsearch successful!')
    yield conn
    conn.transport.close()


class ElasticsearchLoader:
    """
    Класс для загрузки данных
    в подготовленном формате
    в Elasticsearch.
    """
    def __init__(
        self,
        conn: _connection,
        index_name: str,
        schema: dict
    ):
        self._conn = conn
        self._index_name = index_name
        self._schema = schema
        self.create_index()

    @backoff()
    def create_index(self):
        """
        Метод для создания индекса
        в Elasticsearch.
        """
        if not self._conn.indices.exists(self._index_name):
            self._conn.indices.create(index=self._index_name, body=self._schema)
            logger.info('Elasticsearch index %s was created', self._index_name)
        else:
            logger.info('Elasticsearch index %s already exists', self._index_name)

    @backoff()
    def get_data(self, id: str):
        return self._conn.get(index=self._index_name, id=id)

    @backoff()
    def save_data(self, data: Generator, batch_size: int):
        """
        Метод для загрузки
        данных в Elasticsearch.
        """
        count_successful_actions, _ = helpers.bulk(
            client=self._conn,
            index=self._index_name,
            actions=data,
            chunk_size=batch_size,
        )

        logger.info('Saved bath in Elasticsearch index with length %s', count_successful_actions)
