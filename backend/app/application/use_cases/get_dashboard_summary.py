"""Use case: aggregate dashboard metrics."""
from __future__ import annotations

from app.application.dto.dashboard import DashboardSummary
from app.domain.ports import AnalysisRepository


class GetDashboardSummaryUseCase:
    def __init__(self, repository: AnalysisRepository) -> None:
        self._repository = repository

    async def execute(self) -> DashboardSummary:
        return await self._repository.summary()
