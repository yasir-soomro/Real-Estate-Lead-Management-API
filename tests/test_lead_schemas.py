"""Tests for lead request and response schemas."""

import unittest

from pydantic import ValidationError

from real_estate_lead_api.schemas.leads import LeadCreate, LeadResponse, LeadUpdate


class LeadCreateTests(unittest.TestCase):
    def test_create_defaults_status_to_new(self) -> None:
        lead = LeadCreate.model_validate(
            {
                "name": "Amina Khan",
                "phone": "+923001234567",
                "city": "Karachi",
                "budget": 15000000,
            }
        )

        self.assertEqual(lead.status, "new")

    def test_create_accepts_approved_status(self) -> None:
        lead = LeadCreate.model_validate(
            {
                "name": "Amina Khan",
                "phone": "+923001234567",
                "city": "Karachi",
                "budget": 15000000,
                "status": "qualified",
            }
        )

        self.assertEqual(lead.status, "qualified")

    def test_create_rejects_missing_and_empty_required_fields(self) -> None:
        payload = {
            "name": "Amina Khan",
            "phone": "+923001234567",
            "city": "Karachi",
            "budget": 15000000,
        }
        for field in ("name", "phone", "city", "budget"):
            with self.subTest(field=field):
                missing_field = payload.copy()
                del missing_field[field]
                with self.assertRaises(ValidationError):
                    LeadCreate.model_validate(missing_field)

        for field in ("name", "phone", "city"):
            with self.subTest(field=field):
                empty_field = payload.copy()
                empty_field[field] = ""
                with self.assertRaises(ValidationError):
                    LeadCreate.model_validate(empty_field)

    def test_create_rejects_invalid_budgets(self) -> None:
        payload = {
            "name": "Amina Khan",
            "phone": "+923001234567",
            "city": "Karachi",
            "budget": 15000000,
        }
        for budget in (0, -1, 15000000.5, "15000000", True):
            with self.subTest(budget=budget):
                invalid_payload = payload.copy()
                invalid_payload["budget"] = budget
                with self.assertRaises(ValidationError):
                    LeadCreate.model_validate(invalid_payload)

    def test_create_rejects_invalid_status_and_unknown_fields(self) -> None:
        payload = {
            "name": "Amina Khan",
            "phone": "+923001234567",
            "city": "Karachi",
            "budget": 15000000,
        }
        with self.assertRaises(ValidationError):
            LeadCreate.model_validate({**payload, "status": "closed"})
        with self.assertRaises(ValidationError):
            LeadCreate.model_validate({**payload, "source": "website"})


class LeadUpdateTests(unittest.TestCase):
    def test_update_accepts_partial_values(self) -> None:
        update = LeadUpdate.model_validate({"city": "Lahore"})

        self.assertEqual(update.model_dump(exclude_unset=True), {"city": "Lahore"})

    def test_update_rejects_empty_null_and_invalid_values(self) -> None:
        for payload in ({}, {"name": None}, {"budget": 0}, {"status": "closed"}):
            with self.subTest(payload=payload):
                with self.assertRaises(ValidationError):
                    LeadUpdate.model_validate(payload)

    def test_update_rejects_unknown_fields(self) -> None:
        with self.assertRaises(ValidationError):
            LeadUpdate.model_validate({"id": 12})


class LeadResponseTests(unittest.TestCase):
    def test_response_requires_generated_id_and_lead_fields(self) -> None:
        response = LeadResponse.model_validate(
            {
                "id": 12,
                "name": "Amina Khan",
                "phone": "+923001234567",
                "city": "Karachi",
                "budget": 15000000,
                "status": "contacted",
            }
        )

        self.assertEqual(response.id, 12)
        self.assertEqual(response.status, "contacted")


if __name__ == "__main__":
    unittest.main()