from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import get_settings
from backend.app.routes import router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description="Analytics API for Nigeria presidential, gubernatorial, turnout, assembly, and anomaly dashboards.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "healthy", "environment": settings.environment}


app.include_router(router, prefix="/api")
