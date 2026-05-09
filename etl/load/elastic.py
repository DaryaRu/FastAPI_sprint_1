"""Load documents into Elasticsearch."""

import logging

from elasticsearch import Elasticsearch, helpers

from backoff import backoff
from config import Settings
from load.es_schema import MOVIES_INDEX_SCHEMA
from models import FilmWork

logger = logging.getLogger(__name__)


class ElasticsearchWriter:
    """Write ETL docs to Elasticsearch index."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = Elasticsearch(hosts=[settings.elastic_host])

    @backoff()
    def check_or_create_index(self) -> None:
        """Create Elasticsearch index if it does not exist yet."""
        if self.client.indices.exists(index=self.settings.elastic_index):
            logger.info(
                "Elasticsearch index %s already exists",
                self.settings.elastic_index,
            )
            return

        self.client.indices.create(
            index=self.settings.elastic_index,
            body=MOVIES_INDEX_SCHEMA,
        )
        logger.info(
            "Created Elasticsearch index %s", self.settings.elastic_index
        )

    @backoff()
    def bulk_save(self, film_works: list[FilmWork]) -> None:
        """Load a batch of film work docs into Elasticsearch."""
        if not film_works:
            return

        actions = [
            {
                "_index": self.settings.elastic_index,
                "_id": str(film_work.id),
                "_source": film_work.model_dump(mode="json"),
            }
            for film_work in film_works
        ]
        helpers.bulk(self.client, actions)
        logger.info("Uploaded %s film works to Elasticsearch", len(film_works))
