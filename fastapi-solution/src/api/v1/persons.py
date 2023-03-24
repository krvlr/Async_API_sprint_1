import logging
from dataclasses import asdict
from http import HTTPStatus

from fastapi import Query

from models.person import PersonFilters, PersonBrief, PersonDetail
from models.shared import Paginator

logger = logging.getLogger(__name__)
from fastapi import APIRouter, Depends, HTTPException

from services.persons import PersonService, get_person_service

router = APIRouter()


@router.get(
    "/search", response_model=list[PersonBrief], description="Search persons based on title query, filters and sorting"
)
async def person_search(
    query: str | None = None,
    sort: list[str] | None = Query(default=None),
    filters: PersonFilters = Depends(PersonFilters),
    paginator: Paginator = Depends(Paginator),
    person_service: PersonService = Depends(get_person_service),
) -> list[PersonBrief]:
    persons = await person_service.get_by_query(
        query, sort, paginator.page_number, paginator.page_size, asdict(filters)
    )
    return [PersonBrief(**person.dict()) for person in persons]


@router.get("/", response_model=list[PersonBrief], description="Get list of all persons with filters and sorting")
async def person_list(
    sort: list[str] | None = Query(default=None),
    filters: PersonFilters = Depends(PersonFilters),
    paginator: Paginator = Depends(Paginator),
    person_service: PersonService = Depends(get_person_service),
) -> list[PersonBrief]:
    persons = await person_service.get_list(
        sort, paginator.page_number, paginator.page_size, asdict(filters)
    )
    return [PersonBrief(**person.dict()) for person in persons]


@router.get("/{person_id}", response_model=PersonDetail, description="Get single person details")
async def person_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> PersonDetail:
    person = await person_service.get_by_id(person_id, model_cls=PersonDetail)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return person
