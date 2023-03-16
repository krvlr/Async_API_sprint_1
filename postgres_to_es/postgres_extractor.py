from datetime import datetime
from typing import Iterator

import psycopg2
from decorators import backoff
from loguru import logger
from psycopg2.extras import RealDictCursor
from settings import ETL_BATCH_SIZE, POSTGRES_CONNECTION_SETTINGS

FILMWORKS_QUERY = """
        SELECT
           fw.id,
           fw.title,
           fw.description,
           fw.rating as imdb_rating,
           fw.modified,
           COALESCE (
               json_agg(
                   DISTINCT jsonb_build_object(
                       'id', p.id,
                       'name', p.full_name
                   )
               ) FILTER (WHERE p.id is not null and pfw.role = 'actor'),
               '[]'
           ) as actors,
            COALESCE (
               json_agg(
                   DISTINCT jsonb_build_object(
                       'id', p.id,
                       'name', p.full_name
                   )
               ) FILTER (WHERE p.id is not null and pfw.role = 'writer'),
               '[]'
           ) as writers,
           COALESCE (
               json_agg(
                   DISTINCT jsonb_build_object(
                       'id', p.id,
                       'name', p.full_name
                   )
               ) FILTER (WHERE p.id is not null and pfw.role = 'director'),
               '[]'
           ) as directors,
           COALESCE (
               json_agg(
                   DISTINCT jsonb_build_object(
                       'id', g.id,
                       'name', g.name
                   )
               ),
               '[]'
           ) as genres, 
            COALESCE (array_agg(DISTINCT p.full_name) FILTER ( WHERE  pfw.role = 'actor'), '{}') as actors_names,
            COALESCE (array_agg(DISTINCT p.full_name) FILTER ( WHERE  pfw.role = 'writer'), '{}') as writers_names,
            COALESCE (array_agg(DISTINCT p.full_name) FILTER ( WHERE  pfw.role = 'director'), '{}') as directors_names
        FROM content.film_work fw
        LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
        LEFT JOIN content.person p ON p.id = pfw.person_id
        LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
        LEFT JOIN content.genre g ON g.id = gfw.genre_id
        WHERE fw.modified > %s OR p.modified > %s OR g.modified > %s
        GROUP BY fw.id
        """
PERSONS_QUERY = """
        SELECT
            p.id,
            p.full_name,
            COALESCE(
                json_agg(
                    DISTINCT jsonb_build_object(
                                       'id', fw.id,
                                       'roles', COALESCE(
                                           (
                                           SELECT
                                               array_agg(pfw.role)
                                           FROM content.person_film_work pfw
                                           WHERE
                                               pfw.person_id = p.id
                                           AND
                                               pfw.film_work_id = fw.id
                                           ), '{}'
                                           )
                        )
                    ), '[]'
                ) as films
        FROM content.person as p
        LEFT JOIN content.person_film_work pfw ON p.id = pfw.person_id
        LEFT JOIN content.film_work fw ON pfw.film_work_id =fw.id
        WHERE fw.modified > %s OR p.modified > %s
        GROUP BY p.id
        """
GENRES_QUERY = """
        SELECT
            g.id,
            g.name,
            g.description
        FROM content.genre g 
        WHERE g.modified > %s
"""


class PostgresExtractor:
    @backoff()
    def create_connection(self):
        self.connection = psycopg2.connect(
            **POSTGRES_CONNECTION_SETTINGS, cursor_factory=RealDictCursor
        )
        return self.connection

    @backoff()
    def extract_data(self, query: str, param_count: int, date_last_modified: datetime) -> Iterator:
        if not self.connection:
            raise Exception(
                "Не создано подключение к postgresql. Воспользуйтесь create_connection."
            )
        with self.connection.cursor() as cursor:
            cursor.execute(query, (date_last_modified,) * param_count)
            while rows := cursor.fetchmany(ETL_BATCH_SIZE):
                yield rows
