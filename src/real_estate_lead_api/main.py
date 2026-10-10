"""Application entry point."""

import uvicorn
from fastapi import FastAPI

from real_estate_lead_api.config import Settings, get_settings
from real_estate_lead_api.repositories.leads import InMemoryLeadRepository
from real_estate_lead_api.routers.health import router as health_router
from real_estate_lead_api.routers.leads import router as leads_router
from real_estate_lead_api.services.leads import LeadService


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the API application with the provided or environment settings."""
    app_settings = settings if settings is not None else get_settings()
    application = FastAPI(title=app_settings.app_name, debug=app_settings.debug)
    application.state.settings = app_settings
    lead_repository = InMemoryLeadRepository()
    application.state.lead_repository = lead_repository
    application.state.lead_service = LeadService(lead_repository)
    application.include_router(health_router)
    application.include_router(leads_router)
    return application


app = create_app()


def main() -> None:
    """Run the API with Uvicorn."""
    settings: Settings = app.state.settings
    uvicorn.run(
        "real_estate_lead_api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )