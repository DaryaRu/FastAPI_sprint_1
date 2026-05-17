"""Persons API endpoint router.

Provides routes for full-text person search, paginated listing,
fetching person details, and retrieving films associated with a person.
"""

from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache.decorator import cache

from api.v1.dependencies import PaginationParams
from core import config
from schemas.film_shorts import FilmShortResponse as FilmShort
from schemas.persons import Person
from services.persons import PersonService, get_person_service

router = APIRouter()


@router.get(
    "/search",
    response_model=list[Person],
    summary="Полнотекстовый поиск по персонам",
)
@cache(expire=config.CACHE_EXPIRE)
async def person_search(
    query: str = Query(..., description="Имя для поиска"),
    pagination: PaginationParams = Depends(PaginationParams),
    person_service: PersonService = Depends(get_person_service),
) -> list[Person]:
    """Perform a full-text search for persons by name."""
    return await person_service.get_list(
        page_size=pagination.page_size,
        page_number=pagination.page_number,
        query=query,
    )


@router.get(
    "/{person_uuid}/",
    response_model=Person,
    summary="Получить персону по UUID",
)
@cache(expire=config.CACHE_EXPIRE)
async def person_details(
    person_uuid: UUID,
    person_service: PersonService = Depends(get_person_service),
) -> Person:
    """Get detailed information for a specific person by their UUID."""
    person = await person_service.get_by_uuid(person_uuid)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="person not found"
        )
    return person


@router.get(
    "/{person_uuid}/film/",
    response_model=list[FilmShort],
    summary="Получить все фильмы заданной персоны",
)
@cache(expire=config.CACHE_EXPIRE)
async def person_films(
    person_uuid: UUID,
    pagination: PaginationParams = Depends(PaginationParams),
    person_service: PersonService = Depends(get_person_service),
) -> list[FilmShort]:
    """Get all films associated with a specific person."""
    films = await person_service.get_person_films(
        person_uuid,
        page_size=pagination.page_size,
        page_number=pagination.page_number,
    )
    if films is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="person not found"
        )
    return films


@router.get(
    "/", response_model=list[Person], summary="Получить список всех персон"
)
@cache(expire=config.CACHE_EXPIRE)
async def person_list(
    pagination: PaginationParams = Depends(PaginationParams),
    person_service: PersonService = Depends(get_person_service),
) -> list[Person]:
    """Get a paginated list of all persons."""
    return await person_service.get_list(
        page_size=pagination.page_size,
        page_number=pagination.page_number,
        query=None,
    )
