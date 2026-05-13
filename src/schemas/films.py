"""Film model for API."""

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from schemas.genres import GenreBaseSerializer as Genre
from schemas.persons import PersonResponse


class FilmResponse(BaseModel):
    uuid: UUID = Field(validation_alias="id")
    title: str
    imdb_rating: float | None = None
    description: Optional[str] = None
    creation_date: Optional[date] = None
    directors: list[PersonResponse] = []
    actors: list[PersonResponse] = []
    writers: list[PersonResponse] = []
    genre: list[Genre] = Field(default=[], validation_alias="genres")
    file_path: Optional[str] = None
