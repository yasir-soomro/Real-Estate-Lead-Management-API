"""Process-local repository for real-estate leads."""

from real_estate_lead_api.schemas.leads import LeadCreate, LeadResponse, LeadUpdate


class DuplicateLeadPhoneError(ValueError):
    """Raised when another lead already has the same trimmed phone value."""


class InMemoryLeadRepository:
    """Store leads in memory for the lifetime of this repository instance."""

    def __init__(self) -> None:
        self._leads: dict[int, LeadResponse] = {}
        self._next_id = 1

    def create_lead(self, lead: LeadCreate) -> LeadResponse:
        self._ensure_phone_available(lead.phone)

        stored_lead = LeadResponse(id=self._next_id, **lead.model_dump())
        self._leads[self._next_id] = stored_lead
        self._next_id += 1
        return stored_lead.model_copy()

    def list_leads(
        self,
        city: str | None = None,
        limit: int = 10,
    ) -> list[LeadResponse]:
        leads = self._leads.values()
        if city is not None:
            requested_city = city.casefold()
            leads = (lead for lead in leads if lead.city.casefold() == requested_city)
        return [lead.model_copy() for lead in list(leads)[:limit]]

    def get_lead(self, lead_id: int) -> LeadResponse | None:
        lead = self._leads.get(lead_id)
        return lead.model_copy() if lead is not None else None

    def update_lead(
        self,
        lead_id: int,
        update: LeadUpdate,
    ) -> LeadResponse | None:
        current_lead = self._leads.get(lead_id)
        if current_lead is None:
            return None

        changes = update.model_dump(exclude_unset=True)
        if "phone" in changes:
            self._ensure_phone_available(changes["phone"], excluding_id=lead_id)

        updated_lead = LeadResponse.model_validate(
            {**current_lead.model_dump(), **changes}
        )
        self._leads[lead_id] = updated_lead
        return updated_lead.model_copy()

    def delete_lead(self, lead_id: int) -> bool:
        return self._leads.pop(lead_id, None) is not None

    def _ensure_phone_available(
        self,
        phone: str,
        excluding_id: int | None = None,
    ) -> None:
        normalized_phone = phone.strip()
        for lead_id, lead in self._leads.items():
            if lead_id != excluding_id and lead.phone.strip() == normalized_phone:
                raise DuplicateLeadPhoneError("A lead with this phone already exists")