from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PersonFilmResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    uuid: UUID = Field(validation_alias="id")
    roles: List[str]


class Person(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    uuid: UUID = Field(validation_alias="id")
    full_name: str = Field(validation_alias="name")
    films: List[PersonFilmResponse]


class PersonShort(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    uuid: UUID = Field(validation_alias="id")
    full_name: str = Field(validation_alias="name")


PersonResponse = Person
