from datetime import datetime
from time import sleep
from typing import Any

from pydantic import BaseModel

from data_transform import DataTransform
from elasticsearch_loader import ElasticsearchLoader
from loguru import logger
from postgres_extractor import PostgresExtractor, FILMWORKS_QUERY, PERSONS_QUERY, GENRES_QUERY
from es_schema import MOVIES_INDEX, PERSONS_INDEX, GENRE_INDEX
from settings import ETL_REPEAT_INTERVAL_TIME_SEC, REDIS_ADAPTER
from state import RedisStorage, State
from models import ESFilmworkData, ESPersonData, ESGenreData


class ETLHandler:
    PARAMS = {
        'filmwork': {
            'sql_query': FILMWORKS_QUERY,
            'elastic_index_name': 'movies',
            'elastic_index_params': MOVIES_INDEX,
            'transform_model': ESFilmworkData,
            'param_count': 3
        },
        'person': {
            'sql_query': PERSONS_QUERY,
            'elastic_index_name': 'persons',
            'elastic_index_params': PERSONS_INDEX,
            'transform_model': ESPersonData,
            'param_count': 2
        },
        'genre': {
            'sql_query': GENRES_QUERY,
            'elastic_index_name': 'genres',
            'elastic_index_params': GENRE_INDEX,
            'transform_model': ESGenreData,
            'param_count': 1
        }
    }

    @staticmethod
    def get_etl(obj_type):
        return ETLHandler.ETL(**ETLHandler.PARAMS[obj_type])

    class ETL(BaseModel):
        sql_query: str
        elastic_index_name: str
        elastic_index_params: dict
        transform_model: Any
        param_count: int


if __name__ == "__main__":
    state = State(RedisStorage(REDIS_ADAPTER))

    extractor = PostgresExtractor()
    transformer = DataTransform()
    loader = ElasticsearchLoader()

    etl_for = ('filmwork', 'person', 'genre')

    while True:
        try:
            logger.info("Запуск ETL PostgreSQL to Elasticsearch")

            with extractor.create_connection(), loader.create_connection():
                last_modified_datetime = state.get_state("last_modified_datetime") or datetime.min

                for obj_type in etl_for:
                    etl = ETLHandler.get_etl(obj_type)
                    count = 0
                    for data in extractor.extract_data(etl.sql_query, etl.param_count, last_modified_datetime):
                        transformed_data = transformer.validate_and_transform(etl.transform_model, data)
                        loader.load_data(etl.elastic_index_name, etl.elastic_index_params, transformed_data)
                        count += len(transformed_data)
                        logger.info(f"Загружено всего {count} записей для {obj_type}")

                state.set_state(
                    "last_modified_datetime", datetime.now().isoformat()
                )

        except Exception as e:
            logger.error(e)
        finally:
            sleep(ETL_REPEAT_INTERVAL_TIME_SEC)
