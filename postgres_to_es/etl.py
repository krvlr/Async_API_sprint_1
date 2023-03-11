from datetime import datetime
from time import sleep

from data_transform import DataTransform
from elasticsearch_loader import ElasticsearchLoader
from loguru import logger
from postgres_extractor import PostgresExtractor
from settings import ETL_REPEAT_INTERVAL_TIME_SEC, REDIS_ADAPTER
from state import RedisStorage, State

if __name__ == "__main__":
    state = State(RedisStorage(REDIS_ADAPTER))

    extractor = PostgresExtractor()
    transformer = DataTransform()
    loader = ElasticsearchLoader()

    while True:
        try:
            logger.info("Запуск ETL PostgreSQL to Elasticsearch")

            with extractor.create_connection(), loader.create_connection():
                last_modified_datetime = state.get_state("last_modified_datetime")
                last_modified_datetime = (
                    last_modified_datetime if last_modified_datetime else datetime.min
                )

                count = 0
                for movies in extractor.extract_movies(last_modified_datetime):
                    state.set_state(
                        "last_modified_datetime", datetime.now().isoformat()
                    )
                    transformed_movies = transformer.validate_and_transform(movies)
                    loader.load_movies(transformed_movies)
                    count += len(transformed_movies)
                    logger.info(f"Загружено {count} записей")

        except Exception as e:
            logger.error(e)
        finally:
            sleep(ETL_REPEAT_INTERVAL_TIME_SEC)
