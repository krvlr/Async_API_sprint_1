import logging
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio.client import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import PersonDetail, PersonBrief
from services.base import Service
from utils.caching import cache

logger = logging.getLogger(__name__)


class PersonService(Service):
    @cache()
    async def get_by_id(self, obj_id: str, model_cls=PersonDetail) -> PersonDetail | None:
        return await self._get_obj_from_elastic(obj_id, "persons", model_cls)

    async def get_list(
        self, sort: list[str] | None, page_number: int, page_size: int, filters: dict
    ) -> list[PersonBrief]:
        docs = await self.search(
            index="persons",
            model=PersonDetail,
            sort=sort,
            page_number=page_number,
            page_size=page_size,
            filters=filters,
        )
        return [PersonDetail(**doc["_source"]) for doc in docs["hits"]["hits"]]

    async def get_by_query(
        self, query: str, sort: list[str] | None, page_number: int, page_size: int, filters: dict
    ) -> list[PersonDetail]:
        docs = await self.search(
            index="persons",
            model=PersonDetail,
            sort=sort,
            page_number=page_number,
            page_size=page_size,
            filters=filters,
            query=("title", query) if query else None,
        )
        return [PersonDetail(**doc["_source"]) for doc in docs["hits"]["hits"]]


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    person_service = PersonService(redis, elastic)
    person_service.ALLOWED_SORT_FIELDS = {"full_name": "full_name.raw"}
    return person_service
