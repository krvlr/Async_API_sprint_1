from dataclasses import dataclass

import orjson
from fastapi import Query
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


@dataclass
class FilmFilters:
    genres_id: list[str] | None = Query(default=None)
    genres_name: list[str] | None = Query(default=None)
    actors_id: list[str] | None = Query(default=None)
    actors_name: list[str] | None = Query(default=None)
    writers_id: list[str] | None = Query(default=None)
    writers_name: list[str] | None = Query(default=None)
    directors_id: list[str] | None = Query(default=None)
    directors_name: list[str] | None = Query(default=None)


class FilmBrief(BaseModel):
    id: str
    title: str
    imdb_rating: float


class FilmPerson(BaseModel):
    id: str
    name: str


class FilmGenre(BaseModel):
    id: str
    name: str


class FilmDetail(FilmBrief):
    description: str | None
    actors: list[FilmPerson]
    writers: list[FilmPerson]
    directors: list[FilmPerson]
    genres: list[FilmGenre]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
