"""Celery tasks — the async processing entry point.

A task is intentionally thin: it wires up the concrete adapters and delegates to
the `ProcessExamAnalysisUseCase`. All business logic stays in the application /
domain layers, so the same use case can run inline in tests without Celery.
"""
from __future__ import annotations

import asyncio
from uuid import UUID

from app.application.use_cases.process_exam_analysis import (
    ProcessExamAnalysisUseCase,
)
from app.core.config import settings
from app.core.logging import get_logger
from app.infrastructure.ai.predictor import build_inference_engine
from app.infrastructure.database.repositories.analysis_repository import (
    SqlAlchemyAnalysisRepository,
)
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.queue.celery_app import celery_app
from app.infrastructure.storage.local_storage import LocalFileStorage

logger = get_logger(__name__)

# The inference engine is built once per worker process (model load is costly).
_inference_engine = None


def _get_inference_engine():
    global _inference_engine
    if _inference_engine is None:
        _inference_engine = build_inference_engine()
    return _inference_engine


async def _run(analysis_id: UUID) -> None:
    storage = LocalFileStorage(settings.STORAGE_DIR)
    inference = _get_inference_engine()
    async with AsyncSessionLocal() as session:
        repository = SqlAlchemyAnalysisRepository(session)
        use_case = ProcessExamAnalysisUseCase(repository, storage, inference)
        await use_case.execute(analysis_id)
        await session.commit()


@celery_app.task(name="analysis.process", bind=True, max_retries=2)
def process_analysis_task(self, analysis_id: str) -> str:  # noqa: ANN001
    logger.info("Worker received analysis %s", analysis_id)
    try:
        asyncio.run(_run(UUID(analysis_id)))
    except Exception as exc:  # noqa: BLE001
        logger.exception("Task failed for analysis %s", analysis_id)
        raise self.retry(exc=exc, countdown=5) from exc
    return analysis_id


def enqueue_analysis(analysis_id: UUID) -> None:
    """Helper injected into the upload use case to dispatch processing."""
    process_analysis_task.delay(str(analysis_id))
