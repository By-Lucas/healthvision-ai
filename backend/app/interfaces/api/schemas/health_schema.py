from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str
    environment: str
    version: str = "1.0.0"
