"""Use case: list analyses with optional status/class filters."""
from __future__ import annotations

from app.domain.entities.analysis import Analysis, AnalysisStatus
from app.domain.ports import AnalysisRepository
from app.domain.value_objects.prediction import PredictedClass


class ListAnalysisHistoryUseCase:
    def __init__(self, repository: AnalysisRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        *,
        status: AnalysisStatus | None = None,
        predicted_class: PredictedClass | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Analysis]:
        return await self._repository.list(
            status=status,
            predicted_class=predicted_class,
            limit=limit,
            offset=offset,
        )
