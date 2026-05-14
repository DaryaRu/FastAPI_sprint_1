"""Load documents into Elasticsearch."""

import logging

from backoff import backoff
from config import Settings
from elasticsearch import Elasticsearch, helpers
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class ElasticsearchWriter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = Elasticsearch(hosts=[settings.elastic_host])

    @backoff()
    def check_or_create_index(
        self,
        index: str,
        schema: dict,
    ) -> None:
        if self.client.indices.exists(index=index):
            logger.info(
                "Elasticsearch index %s already exists",
                index,
            )
            return

        self.client.indices.create(
            index=index,
            body=schema,
        )

        logger.info(
            "Created Elasticsearch index %s",
            index,
        )

    @backoff()
    def bulk_save(
        self,
        index: str,
        documents: list[BaseModel],
    ) -> None:
        if not documents:
            return

        actions = [
            {
                "_index": index,
                "_id": str(document.id),
                "_source": document.model_dump(mode="json"),
            }
            for document in documents
        ]

        helpers.bulk(self.client, actions)

        logger.info(
            "Uploaded %s documents to index %s",
            len(documents),
            index,
        )
