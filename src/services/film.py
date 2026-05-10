"""Film service: business logic for films."""

from typing import Optional
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from schemas.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        """Return a film by id (using cache when available)."""
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)
        return film

    async def get_list(
        self,
        sort: Optional[str],
        genre: Optional[UUID],
        page_number: int,
        page_size: int,
    ) -> list[Film]:
        """Return a paginated list of films (with sort and genre filter)."""
        query: dict = {"match_all": {}}
        if genre:
            query = {
                "nested": {
                    "path": "genre",
                    "query": {"term": {"genre.uuid": str(genre)}},
                }
            }

        body: dict = {
            "query": query,
            "from": (page_number - 1) * page_size,
            "size": page_size,
        }

        if sort:
            order = "desc" if sort.startswith("-") else "asc"
            field = sort.lstrip("-")
            body["sort"] = [{field: {"order": order}}]

        result = await self.elastic.search(index="movies", body=body)
        return [Film(**hit["_source"]) for hit in result["hits"]["hits"]]

    async def search(
        self,
        query: str,
        page_number: int,
        page_size: int,
    ) -> list[Film]:
        """Search films by query string for title and description fields."""
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "description"],
                }
            },
            "from": (page_number - 1) * page_size,
            "size": page_size,
        }
        result = await self.elastic.search(index="movies", body=body)
        return [Film(**hit["_source"]) for hit in result["hits"]["hits"]]

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        """Return a single film document from Elasticsearch by id."""
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
        except NotFoundError:
            return None
        return Film(**doc["_source"])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        """Return a film from Redis cache, or None if not cached."""
        data = await self.redis.get(film_id)
        if not data:
            return None
        return Film.model_validate_json(data)

    async def _put_film_to_cache(self, film: Film):
        """Store a film in Redis cache."""
        await self.redis.set(
            str(film.uuid),
            film.model_dump_json(),
            ex=FILM_CACHE_EXPIRE_IN_SECONDS,
        )


def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    """FastAPI dependency that returns a FilmService instance."""
    return FilmService(redis, elastic)
