"""Tests for app-scoped dependency instances."""

import unittest

from starlette.requests import Request

from real_estate_lead_api.config import Settings
from real_estate_lead_api.dependencies import (
    get_lead_repository,
    get_lead_service,
)
from real_estate_lead_api.main import create_app
from real_estate_lead_api.schemas.leads import LeadCreate


class LeadDependencyTests(unittest.TestCase):
    def test_repository_and_service_are_shared_across_requests(self) -> None:
        application = create_app(
            Settings(
                app_name="Test API",
                debug=False,
                host="127.0.0.1",
                port=8000,
            )
        )
        first_request = Request({"type": "http", "app": application})
        second_request = Request({"type": "http", "app": application})

        first_repository = get_lead_repository(first_request)
        first_service = get_lead_service(first_request)
        second_repository = get_lead_repository(second_request)
        second_service = get_lead_service(second_request)

        self.assertIs(first_repository, second_repository)
        self.assertIs(first_service, second_service)

        other_application = create_app(
            Settings(
                app_name="Other Test API",
                debug=False,
                host="127.0.0.1",
                port=8001,
            )
        )
        other_request = Request({"type": "http", "app": other_application})
        self.assertIsNot(first_repository, get_lead_repository(other_request))

        created_lead = first_service.create_lead(
            LeadCreate(
                name="Amina Khan",
                phone="+923001234567",
                city="Karachi",
                budget=15000000,
            )
        )
        self.assertEqual(second_service.get_lead(created_lead.id), created_lead)


if __name__ == "__main__":
    unittest.main()