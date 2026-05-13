"""Internal film model."""

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from models.genres import Genre
from models.persons import Person


class Film(BaseModel):
    id: UUID
    title: str
    imdb_rating: Optional[float] = None
    description: Optional[str] = None
    creation_date: Optional[date] = None
    genres: list[Genre] = []
    directors: list[Person] = []
    actors: list[Person] = []
    writers: list[Person] = []
    file_path: Optional[str] = None
