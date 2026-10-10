"""API tests for lead management routes."""

import unittest

from fastapi.testclient import TestClient

from real_estate_lead_api.config import Settings
from real_estate_lead_api.main import create_app


class LeadApiTests(unittest.TestCase):
    def setUp(self) -> None:
        application = create_app(
            Settings(
                app_name="Test API",
                debug=False,
                host="127.0.0.1",
                port=8000,
            )
        )
        self.client = TestClient(application)

    def lead_payload(
        self,
        phone: str = "+923001234567",
        city: str = "Karachi",
    ) -> dict[str, str | int]:
        return {
            "name": "Amina Khan",
            "phone": phone,
            "city": city,
            "budget": 15000000,
        }

    def test_create_and_reject_duplicate_phone(self) -> None:
        response = self.client.post("/leads/", json=self.lead_payload())

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            "id": 1,
            "name": "Amina Khan",
            "phone": "+923001234567",
            "city": "Karachi",
            "budget": 15000000,
            "status": "new",
        })

        duplicate = self.client.post(
            "/leads/",
            json=self.lead_payload(phone=" +923001234567 "),
        )
        self.assertEqual(duplicate.status_code, 409)

    def test_list_filters_city_and_enforces_default_and_limit_bounds(self) -> None:
        for index in range(11):
            response = self.client.post(
                "/leads/",
                json=self.lead_payload(
                    phone=f"+9230012345{index:02d}",
                    city="Karachi" if index < 6 else "Lahore",
                ),
            )
            self.assertEqual(response.status_code, 201)

        default_list = self.client.get("/leads/")
        self.assertEqual(default_list.status_code, 200)
        self.assertEqual(len(default_list.json()), 10)

        filtered_list = self.client.get("/leads/?city=kArAcHi&limit=1")
        self.assertEqual(filtered_list.status_code, 200)
        self.assertEqual(len(filtered_list.json()), 1)
        self.assertEqual(filtered_list.json()[0]["city"], "Karachi")

        for invalid_limit in (0, 101):
            with self.subTest(limit=invalid_limit):
                invalid_response = self.client.get(
                    f"/leads/?limit={invalid_limit}"
                )
                self.assertEqual(invalid_response.status_code, 422)

    def test_retrieve_update_validation_and_missing_leads(self) -> None:
        created = self.client.post("/leads/", json=self.lead_payload())
        lead_id = created.json()["id"]

        retrieved = self.client.get(f"/leads/{lead_id}")
        self.assertEqual(retrieved.status_code, 200)
        self.assertEqual(retrieved.json()["id"], lead_id)

        updated = self.client.patch(
            f"/leads/{lead_id}",
            json={"city": "Lahore", "budget": 20000000},
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["city"], "Lahore")
        self.assertEqual(updated.json()["budget"], 20000000)
        self.assertEqual(updated.json()["name"], "Amina Khan")

        self.assertEqual(
            self.client.patch(f"/leads/{lead_id}", json={}).status_code,
            422,
        )
        self.assertEqual(
            self.client.patch(
                f"/leads/{lead_id}",
                json={"budget": 0},
            ).status_code,
            422,
        )
        self.assertEqual(self.client.get("/leads/999").status_code, 404)
        self.assertEqual(
            self.client.patch("/leads/999", json={"city": "Lahore"}).status_code,
            404,
        )

    def test_duplicate_phone_update_and_invalid_create(self) -> None:
        first = self.client.post("/leads/", json=self.lead_payload())
        second = self.client.post(
            "/leads/",
            json=self.lead_payload(phone="+923001234568"),
        )

        duplicate_update = self.client.patch(
            f"/leads/{second.json()['id']}",
            json={"phone": f" {first.json()['phone']} "},
        )
        self.assertEqual(duplicate_update.status_code, 409)

        invalid_create = self.client.post(
            "/leads/",
            json={**self.lead_payload(phone="+923001234569"), "budget": 0},
        )
        self.assertEqual(invalid_create.status_code, 422)

    def test_delete_returns_no_content_and_missing_leads_return_not_found(self) -> None:
        created = self.client.post("/leads/", json=self.lead_payload())
        lead_id = created.json()["id"]

        deleted = self.client.delete(f"/leads/{lead_id}")
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(deleted.content, b"")
        self.assertEqual(self.client.delete(f"/leads/{lead_id}").status_code, 404)

    def test_created_lead_is_visible_to_later_requests(self) -> None:
        created = self.client.post("/leads/", json=self.lead_payload())
        lead_id = created.json()["id"]

        retrieved = self.client.get(f"/leads/{lead_id}")
        listed = self.client.get("/leads/")

        self.assertEqual(retrieved.status_code, 200)
        self.assertEqual(retrieved.json()["id"], lead_id)
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.json()), 1)


if __name__ == "__main__":
    unittest.main()