from dataclasses import dataclass

import orjson
from fastapi import Query
from pydantic import BaseModel

from models.shared import orjson_dumps


@dataclass
class GenreFilters:
    name: list[str] | None = Query(default=None)


class GenreBrief(BaseModel):
    id: str
    name: str


class GenreDetail(GenreBrief):
    description: str | None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
