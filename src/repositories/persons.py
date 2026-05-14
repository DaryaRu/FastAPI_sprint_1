"""Persons repository."""

from repositories.base import BaseElasticRepository


class PersonsRepository(BaseElasticRepository):
    async def search_persons(
        self,
        query_str: str,
        page_number: int = 1,
        page_size: int = 50,
    ) -> list[dict]:
        query = {"match": {"name": {"query": query_str, "fuzziness": "AUTO"}}}
        return await self.get_filtered(
            query=query,
            page_number=page_number,
            page_size=page_size,
        )
