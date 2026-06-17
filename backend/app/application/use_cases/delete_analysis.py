"""Use case: delete an analysis and its stored image."""
from __future__ import annotations

from uuid import UUID

from app.core.exceptions import AnalysisNotFoundError
from app.core.logging import get_logger
from app.domain.ports import AnalysisRepository, FileStorage

logger = get_logger(__name__)


class DeleteAnalysisUseCase:
    def __init__(self, repository: AnalysisRepository, storage: FileStorage) -> None:
        self._repository = repository
        self._storage = storage

    async def execute(self, analysis_id: UUID) -> None:
        analysis = await self._repository.get(analysis_id)
        if analysis is None:
            raise AnalysisNotFoundError()

        # Best-effort file cleanup — never block the delete on storage errors.
        try:
            self._storage.delete(analysis.stored_filename)
        except Exception:  # noqa: BLE001
            logger.warning("Could not delete file for analysis %s", analysis_id)

        await self._repository.delete(analysis_id)
        logger.info("Deleted analysis %s", analysis_id)
