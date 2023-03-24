from fastapi import Query
from orjson import orjson
from pydantic import BaseModel


class BaseOrjsonModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = lambda v, *, default: orjson.dumps(v, default=default).decode()


class Paginator(BaseModel):
    page_number: int = Query(default=1, ge=0)
    page_size: int = Query(default=20, ge=1, le=50)
