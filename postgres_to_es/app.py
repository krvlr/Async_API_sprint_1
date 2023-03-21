"""Файл с основной логикой ETL."""

import contextlib
import logging.config
import os
from datetime import datetime
from time import sleep

from config.elastic_settings import genre_schema, movie_schema, person_schema
from config.logging import LOGGER_CONFIG
from config.queries import query_genres, query_movies, query_persons
from elasticsearch import Elasticsearch as _elastic_connection
from psycopg2 import OperationalError
from psycopg2.extensions import connection as _postgre_connection
from pydantic import BaseModel
from utils.elastic import ElasticsearchLoader, get_conn_elastic
from utils.models import FilmWork, Genre, Person
from utils.postgresql import PostgresExtractor, get_conn_postgresql
from utils.state import JsonFileStorage, State
from utils.transform import DataTransform

logging.config.dictConfig(LOGGER_CONFIG)
logger = logging.getLogger(__name__)


state = State(JsonFileStorage())


etl_params = [
    ('movies', movie_schema, FilmWork, query_movies),
    ('persons', person_schema, Person, query_persons),
    ('genres', genre_schema, Genre, query_genres),
]


def etl(
    pg_conn: _postgre_connection,
    elastic_conn: _elastic_connection,
    elastic_index: str,
    elastic_schema: str,
    transform_model: BaseModel,
    query: str,
    batch_size: int = 5000,
):
    """
    Основной метод перекачки данных
    из PostgreSQL в Elasticsearch.
    """
    postgres_extractor = PostgresExtractor(pg_conn)
    data_transformer = DataTransform(transform_model)
    elastic_loader = ElasticsearchLoader(
        conn=elastic_conn,
        index_name=elastic_index,
        schema=elastic_schema,
    )

    data_generator = postgres_extractor.get_data_loader(query, batch_size)

    for batch in data_generator:
        logger.info('Extract batch from PostgreSQL with length %s', len(batch))
        batch_transformer = data_transformer.get_batch_transformer(batch)
        elastic_loader.save_data(batch_transformer, batch_size)


def main():
    """
    Используется архитектура ETL-пайплайна
    через один запрос в БД.

    Алгоритм:
        1. Выполняем подключение к БД.
        2. Выполняем запрос.
        3. База данных отвечает ошибкой,
        которую перехватываем.
        4. Выполняем повторное подключение до тех пор,
        пока база данных не ответит успехом.
        Начинаем процесс заново со второго шага.
    """
    dsn = {
        'dbname': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST'),
        'port': os.environ.get('DB_PORT'),
        'options': os.environ.get('DB_OPTIONS'),
    }

    etl_sleep_time = int(os.environ.get('ETL_SLEEP_TIME'))
    elastic_url = os.environ.get('ELASTIC_URL')
    batch_size = int(os.environ.get('BATCH_SIZE'))

    while True:
        logger.info('Started etl process')

        # last_upload = state.get_state('last_upload', default=str(datetime.min))
        last_upload = str(datetime.min)
        start_mark = str(datetime.now())

        with contextlib.closing(get_conn_postgresql(**dsn)) as pg_conn, \
                get_conn_elastic(elastic_url) as elastic_conn:
            try:
                for elastic_index, elastic_schema, transform_model, query in etl_params:
                    etl(
                        pg_conn=pg_conn,
                        elastic_conn=elastic_conn,
                        elastic_index=elastic_index,
                        elastic_schema=elastic_schema,
                        transform_model=transform_model,
                        query=query.format(last_upload),
                        batch_size=batch_size
                    )
                    logger.info(
                        'Successful uploaded modified data for %s index '
                        'from PostgreSQL to Elasticsearch, beginning with time %s!',
                        elastic_index,
                        last_upload
                    )

            except OperationalError as error:
                logger.info('Error etl data from PostgreSQL to Elasticsearch: \n%s', error)
                continue

            state.set_state('last_upload', start_mark)

        logger.info('Started sleeping (%s seconds)', etl_sleep_time)
        sleep(etl_sleep_time)


if __name__ == '__main__':
    main()
