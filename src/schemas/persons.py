from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PersonFilmResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    uuid: UUID = Field(validation_alias="id")
    roles: List[str]


class Person(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    uuid: UUID = Field(validation_alias="id")
    full_name: str = Field(validation_alias="name")
    films: List[PersonFilmResponse]

    @model_validator(mode="before")
    @classmethod
    def convert_model_to_dict(cls, data):
        if isinstance(data, BaseModel):
            return data.model_dump(by_alias=True)
        return data


class PersonShort(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    uuid: UUID = Field(validation_alias="id")
    full_name: str = Field(validation_alias="name")

PersonResponse = Person
