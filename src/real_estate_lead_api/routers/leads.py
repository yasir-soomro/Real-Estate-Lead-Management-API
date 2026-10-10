"""HTTP routes for lead management."""

from typing import Annotated, NoReturn

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from real_estate_lead_api.dependencies import get_lead_service
from real_estate_lead_api.schemas.leads import LeadCreate, LeadResponse, LeadUpdate
from real_estate_lead_api.services.leads import (
    DuplicateLeadError,
    LeadNotFoundError,
    LeadService,
)

router = APIRouter(prefix="/leads", tags=["leads"])


def _raise_api_error(error: LeadNotFoundError | DuplicateLeadError) -> NoReturn:
    if isinstance(error, LeadNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    else:
        status_code = status.HTTP_409_CONFLICT
    raise HTTPException(status_code=status_code, detail=str(error)) from error


@router.post(
    "/",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lead(
    lead: LeadCreate,
    lead_service: Annotated[LeadService, Depends(get_lead_service)],
) -> LeadResponse:
    try:
        return lead_service.create_lead(lead)
    except DuplicateLeadError as error:
        _raise_api_error(error)


@router.get("/", response_model=list[LeadResponse])
def list_leads(
    city: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    lead_service: Annotated[LeadService, Depends(get_lead_service)] = None,
) -> list[LeadResponse]:
    return lead_service.list_leads(city=city, limit=limit)


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    lead_service: Annotated[LeadService, Depends(get_lead_service)],
) -> LeadResponse:
    try:
        return lead_service.get_lead(lead_id)
    except LeadNotFoundError as error:
        _raise_api_error(error)


@router.patch("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    update: LeadUpdate,
    lead_service: Annotated[LeadService, Depends(get_lead_service)],
) -> LeadResponse:
    try:
        return lead_service.update_lead(lead_id, update)
    except (LeadNotFoundError, DuplicateLeadError) as error:
        _raise_api_error(error)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: int,
    lead_service: Annotated[LeadService, Depends(get_lead_service)],
) -> Response:
    try:
        lead_service.delete_lead(lead_id)
    except LeadNotFoundError as error:
        _raise_api_error(error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)