"""Health check endpoint."""

from fastapi import APIRouter

from real_estate_lead_api.schemas.health import HealthResponse
from real_estate_lead_api.services.health import get_health_status

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    return get_health_status()