from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.interfaces.api.schemas.health_schema import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(app=settings.APP_NAME, environment=settings.APP_ENV)
