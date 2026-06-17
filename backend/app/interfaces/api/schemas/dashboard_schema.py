from __future__ import annotations

from pydantic import BaseModel

from app.application.dto.dashboard import DashboardSummary
from app.interfaces.api.schemas.analysis_schema import AnalysisResponse


class DashboardSummaryResponse(BaseModel):
    total_analyses: int
    average_confidence: float
    by_class: dict[str, int]
    by_status: dict[str, int]
    recent_analyses: list[AnalysisResponse]

    @classmethod
    def from_dto(
        cls, summary: DashboardSummary, recent: list[AnalysisResponse]
    ) -> DashboardSummaryResponse:
        return cls(
            total_analyses=summary.total_analyses,
            average_confidence=summary.average_confidence,
            by_class=summary.by_class,
            by_status=summary.by_status,
            recent_analyses=recent,
        )
