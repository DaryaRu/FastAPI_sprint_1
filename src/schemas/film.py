"""Film model."""

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from schemas.genre import Genre
from schemas.person import Person


class Film(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float | None = None
    description: Optional[str] = None
    creation_date: Optional[date] = None
    directors: list[Person] = []
    actors: list[Person] = []
    writers: list[Person] = []
    genre: list[Genre] = []
    file_path: Optional[str] = None
