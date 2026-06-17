"""Use case: run AI inference for a pending analysis and persist the result.

Invoked by the Celery worker. Wraps everything in domain state transitions so a
failure is recorded as FAILED rather than silently lost.
"""
from __future__ import annotations

from uuid import UUID

from app.core.exceptions import AnalysisNotFoundError
from app.core.logging import get_logger
from app.domain.ports import AnalysisRepository, FileStorage
from app.domain.services.ai_inference_service import AIInferenceService

logger = get_logger(__name__)


class ProcessExamAnalysisUseCase:
    def __init__(
        self,
        repository: AnalysisRepository,
        storage: FileStorage,
        inference: AIInferenceService,
    ) -> None:
        self._repository = repository
        self._storage = storage
        self._inference = inference

    async def execute(self, analysis_id: UUID) -> None:
        analysis = await self._repository.get(analysis_id)
        if analysis is None:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found")

        analysis.mark_processing()
        await self._repository.update(analysis)

        try:
            image_bytes = self._storage.read(analysis.stored_filename)
            prediction = self._inference.predict(image_bytes)
            analysis.complete(prediction)
            logger.info(
                "Analysis %s completed: %s (%.2f)",
                analysis.id,
                prediction.predicted_class,
                prediction.confidence_score,
            )
        except Exception as exc:  # noqa: BLE001 - we persist any failure
            analysis.fail(str(exc))
            logger.exception("Analysis %s failed", analysis.id)

        await self._repository.update(analysis)
