"""Use case: fetch a single analysis by id."""
from __future__ import annotations

from uuid import UUID

from app.core.exceptions import AnalysisNotFoundError
from app.domain.entities.analysis import Analysis
from app.domain.ports import AnalysisRepository


class GetAnalysisDetailUseCase:
    def __init__(self, repository: AnalysisRepository) -> None:
        self._repository = repository

    async def execute(self, analysis_id: UUID) -> Analysis:
        analysis = await self._repository.get(analysis_id)
        if analysis is None:
            raise AnalysisNotFoundError()
        return analysis
