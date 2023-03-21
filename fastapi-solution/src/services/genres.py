import logging
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio.client import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import GenreDetail, GenreBrief
from services.base import Service
from utils.caching import cache

logger = logging.getLogger(__name__)


class GenreService(Service):
    @cache()
    async def get_by_id(self, obj_id: str, model_cls=GenreDetail) -> GenreDetail | None:
        return await self._get_obj_from_elastic(obj_id, "genres", model_cls)

    @cache()
    async def get_list(
        self, sort: list[str] | None, page_number: int, page_size: int, filters: dict
    ) -> list[GenreBrief]:
        docs = await self.search(
            index="genres",
            model=GenreBrief,
            sort=sort,
            page_number=page_number,
            page_size=page_size,
            filters=filters,
        )
        return [GenreBrief(**doc["_source"]) for doc in docs["hits"]["hits"]]


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    genre_service = GenreService(redis, elastic)
    genre_service.ALLOWED_SORT_FIELDS = {"name": "name.raw", "description": "description.raw"}
    return genre_service
