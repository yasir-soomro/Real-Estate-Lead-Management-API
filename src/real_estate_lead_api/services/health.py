"""Health check business logic."""

from real_estate_lead_api.schemas.health import HealthResponse


def get_health_status() -> HealthResponse:
    return HealthResponse(status="ok")