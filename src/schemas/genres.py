from uuid import UUID
from pydantic import BaseModel, Field


class GenreBaseSerializer(BaseModel):
    uuid: UUID = Field(validation_alias="id")
    name: str
