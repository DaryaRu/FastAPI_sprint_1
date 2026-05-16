"""Film endpoints."""

from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache.decorator import cache

from core import config
from schemas.film_shorts import FilmShortResponse
from schemas.films import FilmResponse
from services.film import FilmService, get_film_service

router = APIRouter()


@router.get("/search", response_model=list[FilmShortResponse])
@cache(expire=config.CACHE_EXPIRE)
async def films_search(
    query: str = Query(...),
    page_number: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmShortResponse]:
    """Endpoint to search films by query string."""
    films = await film_service.search(query, page_number, page_size)
    return [FilmShortResponse.model_validate(f.model_dump()) for f in films]


@router.get("/{film_id}", response_model=FilmResponse)
async def film_details(
    film_id: UUID,
    film_service: FilmService = Depends(get_film_service),
) -> FilmResponse:
    """Endpoint to return full details for a single film by id."""
    film = await film_service.get_by_id(str(film_id))
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="film not found",
        )
    return FilmResponse.model_validate(film.model_dump())


@router.get("/", response_model=list[FilmShortResponse])
@cache(expire=config.CACHE_EXPIRE)
async def films_list(
    sort: Optional[str] = Query(default=None),
    genre: Optional[UUID] = Query(default=None),
    page_number: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmShortResponse]:
    """Endpoint to return a paginated list of films
    with sort and genre filter."""
    films = await film_service.get_list(sort, genre, page_number, page_size)
    return [FilmShortResponse.model_validate(f.model_dump()) for f in films]
