from dataclasses import dataclass

from fastapi import Query
from pydantic import BaseModel

from models.shared import BaseOrjsonModel


@dataclass
class PersonFilters:
    full_name: list[str] | None = Query(default=None)
    films_id: list[str] | None = Query(default=None)


class PersonFilm(BaseModel):
    id: str
    roles: list[str]


class PersonBrief(BaseOrjsonModel):
    id: str
    full_name: str


class PersonDetail(PersonBrief):
    films: list[PersonFilm]
