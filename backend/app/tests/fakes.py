"""In-memory test doubles implementing the domain ports.

Because the application/domain layers depend only on the port abstractions,
these fakes let us test the full behavior without Postgres, RabbitMQ or a real
filesystem — fast and deterministic.
"""
from __future__ import annotations

from uuid import UUID

from app.application.dto.dashboard import DashboardSummary
from app.domain.entities.analysis import Analysis, AnalysisStatus
from app.domain.ports import AnalysisRepository, FileStorage
from app.domain.value_objects.prediction import PredictedClass


class InMemoryAnalysisRepository(AnalysisRepository):
    def __init__(self) -> None:
        self._store: dict[UUID, Analysis] = {}

    async def add(self, analysis: Analysis) -> Analysis:
        self._store[analysis.id] = analysis
        return analysis

    async def get(self, analysis_id: UUID) -> Analysis | None:
        return self._store.get(analysis_id)

    async def update(self, analysis: Analysis) -> Analysis:
        self._store[analysis.id] = analysis
        return analysis

    async def delete(self, analysis_id: UUID) -> bool:
        return self._store.pop(analysis_id, None) is not None

    async def list(
        self,
        *,
        status: AnalysisStatus | None = None,
        predicted_class: PredictedClass | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Analysis]:
        items = sorted(
            self._store.values(), key=lambda a: a.created_at, reverse=True
        )
        if status is not None:
            items = [a for a in items if a.status is status]
        if predicted_class is not None:
            items = [a for a in items if a.predicted_class is predicted_class]
        return items[offset : offset + limit]

    async def summary(self) -> DashboardSummary:
        items = list(self._store.values())
        scores = [a.confidence_score for a in items if a.confidence_score is not None]
        by_class: dict[str, int] = {}
        by_status: dict[str, int] = {}
        for a in items:
            if a.predicted_class:
                by_class[a.predicted_class.value] = (
                    by_class.get(a.predicted_class.value, 0) + 1
                )
            by_status[a.status.value] = by_status.get(a.status.value, 0) + 1
        return DashboardSummary(
            total_analyses=len(items),
            average_confidence=round(sum(scores) / len(scores), 4) if scores else 0.0,
            by_class=by_class,
            by_status=by_status,
        )


class InMemoryStorage(FileStorage):
    def __init__(self) -> None:
        self._files: dict[str, bytes] = {}

    def save(self, stored_filename: str, data: bytes) -> str:
        self._files[stored_filename] = data
        return f"memory://{stored_filename}"

    def read(self, stored_filename: str) -> bytes:
        return self._files[stored_filename]

    def exists(self, stored_filename: str) -> bool:
        return stored_filename in self._files

    def delete(self, stored_filename: str) -> None:
        self._files.pop(stored_filename, None)
