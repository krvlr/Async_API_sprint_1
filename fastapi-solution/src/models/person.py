from dataclasses import dataclass

import orjson
from pydantic import BaseModel
from fastapi import Query


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


@dataclass
class PersonFilters:
    full_name: list[str] | None = Query(default=None)
    films_id: list[str] | None = Query(default=None)


class PersonBrief(BaseModel):
    id: str
    full_name: str


class PersonFilm(BaseModel):
    id: str
    roles: list[str]


class PersonDetail(BaseModel):
    id: str
    full_name: str
    films: list[PersonFilm]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps