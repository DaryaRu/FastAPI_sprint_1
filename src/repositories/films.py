"""Film repository."""

from repositories.base import BaseElasticRepository


class FilmRepository(BaseElasticRepository):
    async def search_films(
        self,
        query_str: str,
        page_number: int = 1,
        page_size: int = 50,
    ) -> list[dict]:
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
