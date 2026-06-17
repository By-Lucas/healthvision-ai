"""Pydantic schemas (the API's data contract).

These are intentionally separate from domain entities and ORM models. They
define exactly what crosses the HTTP boundary, decoupled from internals.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.entities.analysis import EDUCATIONAL_WARNING, Analysis


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    original_filename: str
    image_path: str
    status: str
    predicted_class: str | None = None
    confidence_score: float | None = None
    explanation: str | None = None
    processing_time_ms: int | None = None
    error_message: str | None = None
    findings: dict[str, float] | None = None
    created_at: datetime
    updated_at: datetime
    warning: str = EDUCATIONAL_WARNING

    @classmethod
    def from_entity(cls, entity: Analysis) -> AnalysisResponse:
        return cls(
            id=entity.id,
            original_filename=entity.original_filename,
            image_path=entity.image_path,
            status=entity.status.value,
            predicted_class=(
                entity.predicted_class.value if entity.predicted_class else None
            ),
            confidence_score=entity.confidence_score,
            explanation=entity.explanation,
            processing_time_ms=entity.processing_time_ms,
            error_message=entity.error_message,
            findings=entity.findings,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            warning=entity.warning,
        )


class AnalysisListResponse(BaseModel):
    items: list[AnalysisResponse]
    count: int
