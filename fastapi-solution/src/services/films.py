import logging
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio.client import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import FilmDetail, FilmBrief
from services.base import Service
from utils.caching import cache

logger = logging.getLogger(__name__)


class FilmService(Service):
    @cache()
    async def get_by_id(self, obj_id: str, model_cls=FilmDetail) -> FilmDetail | None:
        return await self._get_obj_from_elastic(obj_id, "movies", model_cls)

    async def get_list(
        self, sort: list[str] | None, page_number: int, page_size: int, filters: dict
    ) -> list[FilmBrief]:
        docs = await self.search(
            index="movies",
            model=FilmDetail,
            sort=sort,
            page_number=page_number,
            page_size=page_size,
            filters=filters,
        )
        return [FilmDetail(**doc["_source"]) for doc in docs["hits"]["hits"]]

    async def get_by_query(
        self, query: str, sort: list[str] | None, page_number: int, page_size: int, filters: dict
    ) -> list[FilmDetail]:
        docs = await self.search(
            index="movies",
            model=FilmDetail,
            sort=sort,
            page_number=page_number,
            page_size=page_size,
            filters=filters,
            query=("title", query) if query else None,
        )
        return [FilmDetail(**doc["_source"]) for doc in docs["hits"]["hits"]]


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    film_service = FilmService(redis, elastic)
    film_service.ALLOWED_SORT_FIELDS = {"title": "title.raw", "imdb_rating": "imdb_rating"}
    return film_service
