from typing import Optional

from pydantic import BaseModel


class ESFilmworkPersonData(BaseModel):
    id: str
    name: str


class ESFilmworkGenreData(BaseModel):
    id: str
    name: str


class ESFilmworkData(BaseModel):
    id: str
    imdb_rating: Optional[float]
    title: str
    description: Optional[str]
    actors_names: list[str] = []
    writers_names: list[str] = []
    directors_names: list[str] = []
    actors: list[ESFilmworkPersonData] = []
    writers: list[ESFilmworkPersonData] = []
    directors: list[ESFilmworkPersonData] = []
    genres: list[ESFilmworkGenreData] = []


class ESPersonFilmworkData(BaseModel):
    id: str
    roles: list[str] = []


class ESPersonData(BaseModel):
    id: str
    full_name: str
    films: list[ESPersonFilmworkData] = []


class ESGenreData(BaseModel):
    id: str
    name: str
    description: str | None

