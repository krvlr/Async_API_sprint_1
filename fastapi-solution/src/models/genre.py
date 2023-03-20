from dataclasses import dataclass

import orjson
from pydantic import BaseModel
from fastapi import Query


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


@dataclass
class GenreFilters:
    name: list[str] | None = Query(default=None)


class GenreBrief(BaseModel):
    id: str
    name: str


class GenreDetail(BaseModel):
    id: str
    name: str
    description: str | None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps