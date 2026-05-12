"""Film model for API."""

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from schemas.genres import GenreBaseSerializer as Genre
from schemas.person import Person


class Film(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    uuid: UUID = Field(validation_alias="id")
    title: str
    imdb_rating: float | None = None
    description: Optional[str] = None
    creation_date: Optional[date] = None
    directors: list[Person] = []
    actors: list[Person] = []
    writers: list[Person] = []
    genre: list[Genre] = Field(default=[], validation_alias="genres")
    file_path: Optional[str] = None
