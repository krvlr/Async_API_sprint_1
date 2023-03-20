from http import HTTPStatus
import logging
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Query
from models.film import FilmFilters, FilmBrief, FilmDetail
from models.shared import Paginator

from services.films import FilmService, get_film_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get('/search', response_model=list[FilmBrief])
async def film_search(
        query: str | None = None,
        sort: list[str] | None = Query(default=None),
        filters: FilmFilters = Depends(FilmFilters),
        paginator: Paginator = Depends(Paginator),
        film_service: FilmService = Depends(get_film_service)
) -> list[FilmBrief]:
    films = await film_service.get_by_query(
        query,
        sort,
        paginator.page_number,
        paginator.page_size,
        asdict(filters)
    )
    return [FilmBrief(**film.dict()) for film in films]


@router.get('/', response_model=list[FilmBrief])
async def film_list(
        sort: list[str] | None = Query(default=None),
        filters: FilmFilters = Depends(FilmFilters),
        paginator: Paginator = Depends(Paginator),
        film_service: FilmService = Depends(get_film_service)
) -> list[FilmBrief]:
    films = await film_service.get_list(
        sort,
        paginator.page_number,
        paginator.page_size,
        asdict(filters)
    )
    return [FilmBrief(**film.dict()) for film in films]


@router.get('/{film_id}', response_model=FilmDetail)
async def film_details(
        film_id: str,
        film_service: FilmService = Depends(get_film_service)
) -> FilmDetail:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return film
