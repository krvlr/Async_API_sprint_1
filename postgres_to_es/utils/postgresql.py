"""Функции и классы для работы с базой PostgreSQL."""

import logging.config
from typing import Generator

import psycopg2
from config.logging import LOGGER_CONFIG
from psycopg2.extensions import connection as _connection
from psycopg2.extensions import cursor as _cursor
from psycopg2.extras import DictCursor

from .utils import backoff

logging.config.dictConfig(LOGGER_CONFIG)
logger = logging.getLogger(__name__)


@backoff()
def get_conn_postgresql(
    dbname: str,
    user: str,
    password: str,
    host: str,
    port: str,
    options: str = '',
    cursor_factory=DictCursor
) -> _connection:
    """"
    Функция для получения
    коннекта к PostgreSQL.
    """
    logger.info('Try connecting to the PostgreSQL database')
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port,
        options=options,
        cursor_factory=cursor_factory
    )
    logger.info('Connection to the PostgreSQL successful!')
    return conn


class PostgresExtractor:
    """
    Класс для загрузки
    данных из PostgreSQL.
    """
    def __init__(self, conn: _connection):
        self._conn = conn

    def fetchmany_generator(
        self,
        cursor: _cursor,
        batch_size: int = 5000,
    ) -> Generator:
        """
        Метод для получения генератора
        извлечения данных из базы батчами.
        """
        batch_iter = 0
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                logger.info('Data loaded successfully!')
                break
            logger.info('Yield %s batch', batch_iter)
            yield [dict(row) for row in batch]
            batch_iter += 1

    def get_data_loader(
        self,
        query: str,
        batch_size: int = 5000,
    ) -> Generator:
        """
        Метод для получения генератора
        выгрузки данных из PostgreSQL.
        """
        cursor = self._conn.cursor()
        cursor.execute(query)
        data_generator = self.fetchmany_generator(cursor, batch_size)
        return data_generator
