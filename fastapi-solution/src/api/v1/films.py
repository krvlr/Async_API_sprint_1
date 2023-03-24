import logging
from dataclasses import asdict
from http import HTTPStatus

from fastapi import Query

from models.film import FilmFilters, FilmBrief, FilmDetail
from models.shared import Paginator

logger = logging.getLogger(__name__)
from fastapi import APIRouter, Depends, HTTPException

from services.films import FilmService, get_film_service

router = APIRouter()


@router.get(
    "/search", response_model=list[FilmBrief], description="Search films based on title query, filters and sorting"
)
async def film_search(
    query: str | None = None,
    sort: list[str] | None = Query(default=None),
    filters: FilmFilters = Depends(FilmFilters),
    paginator: Paginator = Depends(Paginator),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmBrief]:
    films = await film_service.get_by_query(
        query, sort, paginator.page_number, paginator.page_size, asdict(filters)
    )
    return [FilmBrief(**film.dict()) for film in films]


@router.get("/", response_model=list[FilmBrief], description="Get list of all films with filters and sorting")
async def film_list(
    sort: list[str] | None = Query(default=None),
    filters: FilmFilters = Depends(FilmFilters),
    paginator: Paginator = Depends(Paginator),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmBrief]:
    films = await film_service.get_list(
        sort, paginator.page_number, paginator.page_size, asdict(filters)
    )
    return [FilmBrief(**film.dict()) for film in films]


@router.get("/{film_id}", response_model=FilmDetail, description="Get single film details")
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> FilmDetail:
    film = await film_service.get_by_id(film_id, model_cls=FilmDetail)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return film
