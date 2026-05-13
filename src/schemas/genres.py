"""Genre model for API responses."""

from uuid import UUID

from pydantic import BaseModel, Field


class GenreResponse(BaseModel):
    uuid: UUID = Field(validation_alias="id")
    name: str
