"""Film repository."""

from repositories.base import BaseElasticRepository


class FilmRepository(BaseElasticRepository):
    """Elasticsearch repository for film documents."""

    async def search_films(
        self,
        query_str: str,
        page_number: int,
        page_size: int,
    ) -> list[dict]:
        """Search films by query string across title and description fields."""
        query = {
            "multi_match": {
                "query": query_str,
                "fields": ["title", "description"],
            }
        }
        return await self.get_filtered(
            query=query,
            page_number=page_number,
            page_size=page_size,
        )
