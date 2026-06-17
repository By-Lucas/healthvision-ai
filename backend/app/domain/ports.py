"""Driven ports for persistence and storage.

These abstract base classes are the contracts the application layer relies on.
Concrete adapters live in app/infrastructure. This is the Dependency Inversion
core of the Hexagonal/Clean architecture: inner layers depend on these
abstractions, never on the database or filesystem directly.
"""
from __future__ import annotations

import abc
from uuid import UUID

from app.domain.entities.analysis import Analysis, AnalysisStatus
from app.domain.value_objects.prediction import PredictedClass


class AnalysisRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, analysis: Analysis) -> Analysis: ...

    @abc.abstractmethod
    async def get(self, analysis_id: UUID) -> Analysis | None: ...

    @abc.abstractmethod
    async def update(self, analysis: Analysis) -> Analysis: ...

    @abc.abstractmethod
    async def list(
        self,
        *,
        status: AnalysisStatus | None = None,
        predicted_class: PredictedClass | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Analysis]: ...

    @abc.abstractmethod
    async def delete(self, analysis_id: UUID) -> bool:
        """Delete an analysis. Returns True if a row was removed."""

    @abc.abstractmethod
    async def summary(self) -> DashboardSummary: ...


class FileStorage(abc.ABC):
    @abc.abstractmethod
    def save(self, stored_filename: str, data: bytes) -> str:
        """Persist bytes and return the resolvable path/URI."""

    @abc.abstractmethod
    def read(self, stored_filename: str) -> bytes: ...

    @abc.abstractmethod
    def exists(self, stored_filename: str) -> bool: ...

    @abc.abstractmethod
    def delete(self, stored_filename: str) -> None:
        """Remove a stored file (best-effort; no error if missing)."""


# Imported lazily at bottom to avoid circulars in type hints above.
from app.application.dto.dashboard import DashboardSummary  # noqa: E402
