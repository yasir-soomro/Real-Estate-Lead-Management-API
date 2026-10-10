"""Tests for lead use cases."""

import unittest

from real_estate_lead_api.repositories.leads import InMemoryLeadRepository
from real_estate_lead_api.schemas.leads import LeadCreate, LeadUpdate
from real_estate_lead_api.services.leads import (
    DuplicateLeadError,
    LeadNotFoundError,
    LeadService,
)


class LeadServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = LeadService(InMemoryLeadRepository())

    def create_input(self, phone: str = "+923001234567") -> LeadCreate:
        return LeadCreate(
            name="Amina Khan",
            phone=phone,
            city="Karachi",
            budget=15000000,
        )

    def test_service_supports_create_list_get_update_and_delete(self) -> None:
        created = self.service.create_lead(self.create_input())
        self.assertEqual(self.service.get_lead(created.id), created)
        self.assertEqual(self.service.list_leads(), [created])

        updated = self.service.update_lead(
            created.id,
            LeadUpdate(city="Lahore"),
        )
        self.assertEqual(updated.city, "Lahore")
        self.assertIsNone(self.service.delete_lead(created.id))
        self.assertEqual(self.service.list_leads(), [])

    def test_service_raises_not_found_for_get_update_and_delete(self) -> None:
        with self.assertRaises(LeadNotFoundError):
            self.service.get_lead(99)
        with self.assertRaises(LeadNotFoundError):
            self.service.update_lead(99, LeadUpdate(city="Lahore"))
        with self.assertRaises(LeadNotFoundError):
            self.service.delete_lead(99)

    def test_service_translates_duplicate_create_and_update_errors(self) -> None:
        first = self.service.create_lead(self.create_input())
        second = self.service.create_lead(self.create_input(phone="+923001234568"))

        with self.assertRaises(DuplicateLeadError):
            self.service.create_lead(self.create_input(phone=" +923001234567 "))
        with self.assertRaises(DuplicateLeadError):
            self.service.update_lead(
                second.id,
                LeadUpdate(phone=f" {first.phone} "),
            )


if __name__ == "__main__":
    unittest.main()