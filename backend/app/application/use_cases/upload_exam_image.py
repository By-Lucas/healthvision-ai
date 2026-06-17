"""Use case: validate and persist an uploaded exam image, then enqueue analysis.

Orchestrates domain services and ports; contains no framework code. The actual
async dispatch is injected as a callable so this use case stays testable without
a running broker.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from app.core.logging import get_logger
from app.core.security import secure_stored_filename
from app.domain.entities.analysis import Analysis
from app.domain.ports import AnalysisRepository, FileStorage
from app.domain.services.image_validation_service import ImageValidationService

logger = get_logger(__name__)


@dataclass
class UploadExamImageInput:
    filename: str
    content_type: str | None
    data: bytes


class UploadExamImageUseCase:
    def __init__(
        self,
        repository: AnalysisRepository,
        storage: FileStorage,
        validator: ImageValidationService,
        enqueue_analysis: Callable[[UUID], None],
    ) -> None:
        self._repository = repository
        self._storage = storage
        self._validator = validator
        self._enqueue_analysis = enqueue_analysis

    async def execute(self, data_in: UploadExamImageInput) -> Analysis:
        self._validator.validate(
            filename=data_in.filename,
            content_type=data_in.content_type,
            data=data_in.data,
        )

        stored_filename = secure_stored_filename(data_in.filename)
        self._storage.save(stored_filename, data_in.data)
        # Public, frontend-resolvable URL (served by /uploads static mount, or a
        # CDN/S3 URL in production). The worker reads bytes via stored_filename,
        # so this path is purely for display.
        image_path = f"/uploads/{stored_filename}"

        analysis = Analysis(
            original_filename=data_in.filename,
            stored_filename=stored_filename,
            image_path=image_path,
        )
        analysis = await self._repository.add(analysis)
        logger.info("Created analysis %s (status=%s)", analysis.id, analysis.status)

        # Hand off to the async worker. The use case does not care whether this
        # is Celery, an in-process task, or anything else.
        self._enqueue_analysis(analysis.id)
        return analysis
