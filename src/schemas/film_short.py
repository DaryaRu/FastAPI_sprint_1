"""FilmShort model for API."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class FilmShort(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: Optional[float] = None
