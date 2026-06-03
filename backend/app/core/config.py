from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _split_csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    app_name: str = "Nigeria Election Analytics API"
    environment: str = os.getenv("APP_ENV", "development")
    cors_origins: tuple[str, ...] = _split_csv(
        os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,"
            "http://localhost:3001,http://127.0.0.1:3001",
        )
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
