from dataclasses import dataclass

from fastapi import Query

from models.shared import BaseOrjsonModel


@dataclass
class GenreFilters:
    name: list[str] | None = Query(default=None)


class GenreBrief(BaseOrjsonModel):
    id: str
    name: str


class GenreDetail(GenreBrief):
    description: str | None
