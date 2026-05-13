"""FilmShort model for API."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FilmShortResponse(BaseModel):
    uuid: UUID = Field(validation_alias="id")
    title: str
    imdb_rating: Optional[float] = None
