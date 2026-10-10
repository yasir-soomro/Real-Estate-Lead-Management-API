"""Tests for the application entry point."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from starlette.requests import Request

from real_estate_lead_api.config import Settings, get_settings
from real_estate_lead_api.dependencies import get_app_settings
from real_estate_lead_api.main import app, create_app


class HealthEndpointTests(unittest.TestCase):
    def test_health_endpoint_returns_ok(self) -> None:
        response = TestClient(app).get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_app_factory_uses_configured_settings(self) -> None:
        settings = Settings(
            app_name="Test API",
            debug=True,
            host="0.0.0.0",
            port=9000,
        )
        application = create_app(settings)
        request = Request({"type": "http", "app": application})

        self.assertEqual(application.title, "Test API")
        self.assertTrue(application.debug)
        self.assertIs(get_app_settings(request), settings)


class SettingsTests(unittest.TestCase):
    def test_get_settings_uses_defaults(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            settings = get_settings()

        self.assertEqual(settings.app_name, "Real Estate Lead API")
        self.assertFalse(settings.debug)
        self.assertEqual(settings.host, "127.0.0.1")
        self.assertEqual(settings.port, 8000)

    def test_get_settings_reads_environment_overrides(self) -> None:
        environment = {
            "APP_NAME": "Configured API",
            "DEBUG": "true",
            "HOST": "0.0.0.0",
            "PORT": "9000",
        }
        with patch.dict("os.environ", environment, clear=True):
            settings = get_settings()

        self.assertEqual(settings.app_name, "Configured API")
        self.assertTrue(settings.debug)
        self.assertEqual(settings.host, "0.0.0.0")
        self.assertEqual(settings.port, 9000)


if __name__ == "__main__":
    unittest.main()