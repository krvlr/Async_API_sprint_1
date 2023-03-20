"""Классы для валидации формата данных, выгруженных из Postgres."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class PersonFilmWork(BaseModel):
    id: UUID
    name: str


class FilmWork(BaseModel):
    id: UUID
    imdb_rating: float
    genre: List[str]
    title: str
    description: str
    director: List[str]
    actors_names: List[str]
    writers_names: List[str]
    actors: List[PersonFilmWork]
    writers: List[PersonFilmWork]

    @staticmethod
    def custom_validate(**kwargs):
        return FilmWork(
            id=kwargs["id"],
            imdb_rating=kwargs["imdb_rating"],
            genre=kwargs["genre"],
            title=kwargs["title"],
            description=kwargs["description"],
            director=kwargs['director'],
            actors_names=kwargs['actors_names'],
            writers_names=kwargs['writers_names'],
            actors=[PersonFilmWork(**row) for row in kwargs['actors']],
            writers=[PersonFilmWork(**row) for row in kwargs['writers']]
        )


class PersonRoles(BaseModel):
    id: UUID
    roles: List[str]


class Person(BaseModel):
    id: UUID
    full_name: str
    films: List[PersonRoles]

    @staticmethod
    def custom_validate(**kwargs):
        return Person(
            id=kwargs['id'],
            full_name=kwargs['full_name'],
            films=[PersonRoles(**row) for row in kwargs['films']]
        )


class Genre(BaseModel):
    id: UUID
    name: str
    description: Optional[str]

    @staticmethod
    def custom_validate(**kwargs):
        return Genre(
            id=kwargs['id'],
            name=kwargs['name'],
            description=kwargs['description']
        )
