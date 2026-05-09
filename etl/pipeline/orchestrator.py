"""Manage ETL pipeline execution."""

import logging
import time

from config import Settings
from extract.postgres_extractor import (
    DEFAULT_ID_VALUE,
    DEFAULT_MODIFIED_VALUE,
    ENTITY_TYPE_FILM_WORK,
    ENTITY_TYPE_GENRE,
    ENTITY_TYPE_PERSON,
    CheckpointState,
    PostgresExtractor,
    iter_batches,
)
from load.elastic import ElasticsearchWriter
from state.state import State

logger = logging.getLogger(__name__)

ENTITY_TYPES = {
    ENTITY_TYPE_FILM_WORK: "film_work_modified",
    ENTITY_TYPE_GENRE: "genre_modified",
    ENTITY_TYPE_PERSON: "person_modified",
}


class EtlOrchestrator:
    """Manage ETL pipeline stages."""

    def __init__(
        self,
        settings: Settings,
        state: State,
        extractor: PostgresExtractor,
        writer: ElasticsearchWriter,
    ) -> None:
        self.settings = settings
        self.state = state
        self.extractor = extractor
        self.writer = writer

    def run_forever(self) -> None:
        """Run ETL continuously with pauses between cycles."""
        while True:
            self.run_once()
            time.sleep(self.settings.etl_poll_interval)

    def run_once(self) -> None:
        """Run one ETL cycle for all changed entity types."""
        for entity_type, state_key in ENTITY_TYPES.items():
            checkpoint_state = get_checkpoint_state(
                self.state.get_state(state_key)
            )
            film_works, next_checkpoint = self.extractor.extract(
                entity_type, checkpoint_state
            )
            if not film_works:
                logger.debug(
                    "No modified film works found for entity type %s",
                    entity_type,
                )
                continue

            for batch in iter_batches(
                film_works, self.settings.etl_chunk_size
            ):
                self.writer.bulk_save(batch)

            if next_checkpoint:
                self.state.set_state(state_key, next_checkpoint)
                logger.info(
                    "Checkpoint saved for %s: %s",
                    entity_type,
                    next_checkpoint,
                )


def get_checkpoint_state(
    stored_state: CheckpointState | None,
) -> CheckpointState:
    """Normalize state to a checkpoint with modified and id."""

    if stored_state is None:
        result = {
            "modified": DEFAULT_MODIFIED_VALUE,
            "id": DEFAULT_ID_VALUE,
        }
        return result

    result = {
        "modified": stored_state["modified"],
        "id": stored_state["id"],
    }
    return result
