from pydantic import BaseModel
from fastapi import Query


class Paginator(BaseModel):
    page_number: int = 1
    page_size: int = Query(default=20, ge=1, le=50)
