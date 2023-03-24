import logging
from dataclasses import asdict
from http import HTTPStatus

from fastapi.params import Query

from models.genre import GenreDetail, GenreBrief, GenreFilters
from models.shared import Paginator
from services.genres import GenreService, get_genre_service

logger = logging.getLogger(__name__)
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


@router.get("/", response_model=list[GenreBrief], description="Get list of all genres with filters and sorting")
async def genre_list(
    sort: list[str] | None = Query(default=None),
    filters: GenreFilters = Depends(GenreFilters),
    paginator: Paginator = Depends(Paginator),
    genre_service: GenreService = Depends(get_genre_service),
) -> list[GenreBrief]:
    genres = await genre_service.get_list(
        sort, paginator.page_number, paginator.page_size, filters=asdict(filters)
    )
    return [GenreBrief(**genre.dict()) for genre in genres]


@router.get("/{genre_id}", response_model=GenreDetail, description="Get single genre details")
async def genre_details(
    genre_id: str, genre_service: GenreService = Depends(get_genre_service)
) -> GenreDetail:
    genre = await genre_service.get_by_id(genre_id, model_cls=GenreDetail)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
    return genre
