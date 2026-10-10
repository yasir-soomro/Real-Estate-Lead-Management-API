"""Reusable FastAPI dependencies."""

from fastapi import Request

from real_estate_lead_api.config import Settings
from real_estate_lead_api.repositories.leads import InMemoryLeadRepository
from real_estate_lead_api.services.leads import LeadService


def get_app_settings(request: Request) -> Settings:
    """Provide the settings instance configured for this application."""
    return request.app.state.settings


def get_lead_repository(request: Request) -> InMemoryLeadRepository:
    """Provide the repository instance owned by this application."""
    return request.app.state.lead_repository


def get_lead_service(request: Request) -> LeadService:
    """Provide the service instance owned by this application."""
    return request.app.state.lead_service