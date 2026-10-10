"""Tests for in-memory lead storage."""

import unittest

from real_estate_lead_api.repositories.leads import (
    DuplicateLeadPhoneError,
    InMemoryLeadRepository,
)
from real_estate_lead_api.schemas.leads import LeadCreate, LeadUpdate


class InMemoryLeadRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryLeadRepository()

    def create_lead(
        self,
        phone: str = "+923001234567",
        city: str = "Karachi",
    ) -> LeadCreate:
        return LeadCreate(
            name="Amina Khan",
            phone=phone,
            city=city,
            budget=15000000,
        )

    def store_lead(
        self,
        phone: str = "+923001234567",
        city: str = "Karachi",
    ):
        return self.repository.create_lead(self.create_lead(phone=phone, city=city))

    def test_create_assigns_ids_and_retrieves_lead(self) -> None:
        first = self.store_lead()
        second = self.store_lead(phone="+923001234568")

        self.assertEqual(first.id, 1)
        self.assertEqual(first.status, "new")
        self.assertEqual(second.id, 2)
        self.assertEqual(self.repository.get_lead(first.id), first)

    def test_list_filters_city_case_insensitively_and_applies_limit(self) -> None:
        self.store_lead(city="Karachi")
        self.store_lead(phone="+923001234568", city="karachi")
        self.store_lead(phone="+923001234569", city="Lahore")

        leads = self.repository.list_leads(city="KARACHI", limit=1)

        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0].city, "Karachi")

    def test_create_rejects_duplicate_phone_after_trimming(self) -> None:
        self.store_lead(phone=" +923001234567 ")

        with self.assertRaises(DuplicateLeadPhoneError):
            self.store_lead(phone="+923001234567")

    def test_update_applies_partial_changes_and_preserves_other_fields(self) -> None:
        created = self.store_lead()

        updated = self.repository.update_lead(
            created.id,
            LeadUpdate(city="Lahore", budget=20000000),
        )

        self.assertIsNotNone(updated)
        self.assertEqual(updated.city, "Lahore")
        self.assertEqual(updated.budget, 20000000)
        self.assertEqual(updated.name, created.name)
        self.assertEqual(updated.phone, created.phone)

    def test_update_rejects_duplicate_phone_but_allows_unchanged_phone(self) -> None:
        first = self.store_lead(phone="+923001234567")
        second = self.store_lead(phone="+923001234568")

        unchanged = self.repository.update_lead(
            first.id,
            LeadUpdate(phone=" +923001234567 "),
        )
        self.assertEqual(unchanged.phone, " +923001234567 ")

        with self.assertRaises(DuplicateLeadPhoneError):
            self.repository.update_lead(
                second.id,
                LeadUpdate(phone="  +923001234567  "),
            )

    def test_missing_records_and_delete_behavior(self) -> None:
        self.assertIsNone(self.repository.get_lead(99))
        self.assertIsNone(self.repository.update_lead(99, LeadUpdate(city="Lahore")))
        self.assertFalse(self.repository.delete_lead(99))

        lead = self.store_lead()
        self.assertTrue(self.repository.delete_lead(lead.id))
        self.assertIsNone(self.repository.get_lead(lead.id))
        self.assertFalse(self.repository.delete_lead(lead.id))

    def test_returned_leads_cannot_mutate_repository_state(self) -> None:
        lead = self.store_lead()
        lead.city = "Mutated outside repository"

        stored_lead = self.repository.get_lead(lead.id)
        self.assertEqual(stored_lead.city, "Karachi")


if __name__ == "__main__":
    unittest.main()