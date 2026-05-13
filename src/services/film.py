"""Film service: business logic for films."""

from typing import Optional
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from exceptions import ObjectNotFoundException
from models.films import Film
from repositories.film import FilmRepository

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: Redis, repository: FilmRepository):
        self.redis = redis
        self.repository = repository

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        """Return a film by id (using cache when available)."""
        film = await self._film_from_cache(film_id)
        if not film:
            try:
                data = await self.repository.get_by_id(film_id)
            except ObjectNotFoundException:
                return None
            film = Film(**data)
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
        query: dict | None = None
        if genre:
            query = {
                "nested": {
                    "path": "genres",
                    "query": {"term": {"genres.id": str(genre)}},
                }
            }

        sort_param: dict | None = None
        if sort:
            order = "desc" if sort.startswith("-") else "asc"
            field = sort.lstrip("-")
            sort_param = {field: {"order": order}}

        data = await self.repository.get_filtered(
            sort=sort_param,
            query=query,
            page_number=page_number,
            page_size=page_size,
        )
        return self._convert_to_films(data)

    async def search(
        self,
        query: str,
        page_number: int,
        page_size: int,
    ) -> list[Film]:
        """Search films by query string for title and description fields."""
        data = await self.repository.search_films(
            query_str=query,
            page_number=page_number,
            page_size=page_size,
        )
        return self._convert_to_films(data)

    def _convert_to_films(self, data: list[dict]) -> list[Film]:
        """Convert a list of raw dicts to Film objects."""
        return [Film(**item) for item in data]

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        """Return a film from Redis cache, or None if not cached."""
        data = await self.redis.get(film_id)
        if not data:
            return None
        return Film.model_validate_json(data)

    async def _put_film_to_cache(self, film: Film):
        """Store a film in Redis cache."""
        await self.redis.set(
            str(film.id),
            film.model_dump_json(),
            ex=FILM_CACHE_EXPIRE_IN_SECONDS,
        )


def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    """FastAPI dependency that returns a FilmService instance."""
    repository = FilmRepository(elastic, index="movies")
    return FilmService(redis, repository)
