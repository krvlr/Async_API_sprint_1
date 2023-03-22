import logging
from copy import deepcopy
from enum import Enum
from typing import Any, Type

from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import BaseModel
from pydantic.main import ModelMetaclass
from redis.asyncio.client import Redis

from models.film import FilmDetail

logger = logging.getLogger(__name__)


class SortingOrder(Enum):
    ASC = "asc"
    DESC = "desc"


class Service:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.ALLOWED_SORT_FIELDS = dict()

    async def _get_obj_from_elastic(
        self, obj_id: str, index: str, model_cls: Type[FilmDetail]
    ) -> BaseModel | None:
        try:
            doc = await self.elastic.get(index, obj_id)
        except NotFoundError:
            return None
        return model_cls(**doc["_source"])

    async def search(
        self,
        index: str,
        model: Type[BaseModel],
        sort: list[str] | None,
        page_number: int,
        page_size: int,
        filters: dict[str, list | None],
        query: tuple[str, str] | None = None,
    ) -> list[BaseModel]:
        if query:
            field, query = query
            query = {
                "query": {
                    "bool": {"must": {"match": {field: {"query": query, "fuzziness": "auto"}}}}
                }
            }
        else:
            query = {"query": {"bool": {"must": {"match_all": {}}}}}

        filters = {k: v for k, v in filters.items() if v is not None}

        query = self._add_query_filters(query, filters, model)
        logger.info(f"Elastic query: {query}")

        docs = await self.elastic.search(
            index=index,
            body=query,
            from_=(page_number - 1) * page_size,
            size=page_size,
            sort=self._make_sort_string(sort, model),
        )
        return docs

    def _make_sort_string(self, sort_fields: list[str] | None, model: BaseModel) -> str:
        sort_list = ["id:desc"]

        if sort_fields is None:
            return ",".join(sort_list)

        for field in sort_fields:
            sort_order = (
                SortingOrder.DESC.value if field.startswith("-") else SortingOrder.ASC.value
            )
            sort_by = field.strip("-")
            if sort_by in model.__fields__ and sort_by in self.ALLOWED_SORT_FIELDS:
                sort_list.append(f"{self.ALLOWED_SORT_FIELDS[sort_by]}:{sort_order}")
        return ",".join(sort_list)

    def _add_query_filters(self, query: dict, filters: dict, model: Type[BaseModel]) -> dict:
        query_filters = list()

        for filter_field, values in filters.items():
            if path := self._generate_filter_path(filter_field, model):
                query_filter = self._generate_filter(path, values)
                query_filters.append(query_filter)

        if query_filters:
            query["query"]["bool"]["filter"] = query_filters

        return query

    def _generate_filter(self, path: list, values: Any):
        inner_insert = {"nested": {"path": str(), "query": {}}}
        f = dict()
        curr = f

        for i in range(1, len(path)):
            curr.update(deepcopy(inner_insert))
            curr["nested"]["path"] = ".".join(path[:i])
            curr = curr["nested"]["query"]
        curr.update({"terms": {".".join(path): values}})

        return f

    def _generate_filter_path(self, filter_path: list, root_model: Type[BaseModel]):
        path = list()
        while filter_path:
            path_field = str()

            for field_name, field in root_model.__fields__.items():
                if filter_path.startswith(field_name):
                    path_field = field_name
                    filter_path = filter_path.lstrip(field_name).lstrip("_")

                    if isinstance(field.type_, ModelMetaclass):
                        root_model = field.type_

            if not path_field:
                logger.warning(f"Invalid filter path: {filter_path}")
                return

            path.append(path_field)

        return path
