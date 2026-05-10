"""Film endpoints."""

from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from schemas.film import Film
from services.film import FilmService, get_film_service

router = APIRouter()


class FilmShort(BaseModel):
    id: UUID
    title: str
    imdb_rating: Optional[float] = None


def convert_to_short(films: list[Film]) -> list[FilmShort]:
    """Convert a list of Film objects to a list of FilmShort objects."""
    return [
        FilmShort(id=f.uuid, title=f.title, imdb_rating=f.imdb_rating) for f in films
    ]


@router.get("/search", response_model=list[FilmShort])
async def films_search(
    query: str = Query(...),
    page_number: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmShort]:
    """Endpoint to search films by query string."""
    films = await film_service.search(query, page_number, page_size)
    return convert_to_short(films)


@router.get("/{film_id}", response_model=Film)
async def film_details(
    film_id: UUID,
    film_service: FilmService = Depends(get_film_service),
) -> Film:
    """Endpoint to return full details for a single film by id."""
    film = await film_service.get_by_id(str(film_id))
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="film not found",
        )
    return film


@router.get("/", response_model=list[FilmShort])
async def films_list(
    sort: Optional[str] = Query(default=None),
    genre: Optional[UUID] = Query(default=None),
    page_number: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmShort]:
    """Endpoint to return a paginated list of films
    with sort and genre filter."""
    films = await film_service.get_list(sort, genre, page_number, page_size)
    return convert_to_short(films)
