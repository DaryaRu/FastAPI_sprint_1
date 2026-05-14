from typing import List
from uuid import UUID

from pydantic import BaseModel


class PersonFilmShort(BaseModel):
    id: UUID
    roles: List[str]


class Person(BaseModel):
    id: UUID
    name: str
    films: List[PersonFilmShort] = []
