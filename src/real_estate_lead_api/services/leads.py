"""Lead use cases and service-level errors."""

from real_estate_lead_api.repositories.leads import (
    DuplicateLeadPhoneError,
    InMemoryLeadRepository,
)
from real_estate_lead_api.schemas.leads import LeadCreate, LeadResponse, LeadUpdate


class LeadNotFoundError(LookupError):
    """Raised when an operation references a lead that does not exist."""


class DuplicateLeadError(ValueError):
    """Raised when a lead conflicts with an existing phone value."""


class LeadService:
    """Coordinate lead use cases without depending on HTTP behavior."""

    def __init__(self, repository: InMemoryLeadRepository) -> None:
        self._repository = repository

    def create_lead(self, lead: LeadCreate) -> LeadResponse:
        try:
            return self._repository.create_lead(lead)
        except DuplicateLeadPhoneError as error:
            raise DuplicateLeadError(str(error)) from error

    def list_leads(
        self,
        city: str | None = None,
        limit: int = 10,
    ) -> list[LeadResponse]:
        return self._repository.list_leads(city=city, limit=limit)

    def get_lead(self, lead_id: int) -> LeadResponse:
        lead = self._repository.get_lead(lead_id)
        if lead is None:
            raise LeadNotFoundError(f"Lead {lead_id} was not found")
        return lead

    def update_lead(self, lead_id: int, update: LeadUpdate) -> LeadResponse:
        try:
            lead = self._repository.update_lead(lead_id, update)
        except DuplicateLeadPhoneError as error:
            raise DuplicateLeadError(str(error)) from error

        if lead is None:
            raise LeadNotFoundError(f"Lead {lead_id} was not found")
        return lead

    def delete_lead(self, lead_id: int) -> None:
        if not self._repository.delete_lead(lead_id):
            raise LeadNotFoundError(f"Lead {lead_id} was not found")