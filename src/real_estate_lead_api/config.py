"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str
    debug: bool
    host: str
    port: int


def get_settings() -> Settings:
    """Build application settings from the environment."""
    return Settings(
        app_name=os.getenv("APP_NAME", "Real Estate Lead API"),
        debug=os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"},
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
    )