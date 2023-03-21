from http import HTTPStatus

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from loguru import logger
from pydantic import BaseModel

from decorators import backoff
from settings import ELASTIC_SEARCH_URL


class ElasticsearchLoader:
    @backoff()
    def create_connection(self):
        self.client = Elasticsearch(ELASTIC_SEARCH_URL)
        return self.client

    @backoff()
    def _create_index(self, index_name: str, index_params: dict) -> None:
        self.client.indices.create(
            index=index_name,
            ignore=HTTPStatus.BAD_REQUEST,
            body=index_params,
        )
        logger.debug("Индекс для movies создан")

    @backoff()
    def load_data(self, index_name: str, index_params: dict, data: list[BaseModel]) -> None:
        if not self.client:
            raise Exception(
                "Клиент elasticsearch не инициализирован. Воспользуйтесь create_connection."
            )

        if not self.client.indices.exists(index=index_name):
            self._create_index(index_name, index_params)

        documents = [{"_index": index_name, "_id": row.id, "_source": row.dict()} for row in data]
        bulk(self.client, documents)
