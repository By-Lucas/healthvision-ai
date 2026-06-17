"""FastAPI dependency wiring (the composition root for HTTP requests).

This is where abstract ports are bound to concrete adapters. Keeping it in one
place makes the dependency graph explicit and easy to override in tests.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.delete_analysis import DeleteAnalysisUseCase
from app.application.use_cases.get_analysis_detail import GetAnalysisDetailUseCase
from app.application.use_cases.get_dashboard_summary import (
    GetDashboardSummaryUseCase,
)
from app.application.use_cases.list_analysis_history import (
    ListAnalysisHistoryUseCase,
)
from app.application.use_cases.upload_exam_image import UploadExamImageUseCase
from app.core.config import settings
from app.domain.ports import AnalysisRepository, FileStorage
from app.domain.services.image_validation_service import ImageValidationService
from app.infrastructure.database.repositories.analysis_repository import (
    SqlAlchemyAnalysisRepository,
)
from app.infrastructure.database.session import get_async_session
from app.infrastructure.queue.tasks import enqueue_analysis
from app.infrastructure.storage.local_storage import LocalFileStorage

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


def get_repository(session: SessionDep) -> AnalysisRepository:
    return SqlAlchemyAnalysisRepository(session)


RepositoryDep = Annotated[AnalysisRepository, Depends(get_repository)]


def get_storage() -> FileStorage:
    return LocalFileStorage(settings.STORAGE_DIR)


StorageDep = Annotated[FileStorage, Depends(get_storage)]


def get_validator() -> ImageValidationService:
    return ImageValidationService(
        allowed_extensions=settings.ALLOWED_EXTENSIONS,
        allowed_content_types=settings.ALLOWED_CONTENT_TYPES,
        max_bytes=settings.max_upload_bytes,
    )


ValidatorDep = Annotated[ImageValidationService, Depends(get_validator)]


def get_upload_use_case(
    repository: RepositoryDep, storage: StorageDep, validator: ValidatorDep
) -> UploadExamImageUseCase:
    return UploadExamImageUseCase(
        repository=repository,
        storage=storage,
        validator=validator,
        enqueue_analysis=enqueue_analysis,
    )


def get_list_use_case(repository: RepositoryDep) -> ListAnalysisHistoryUseCase:
    return ListAnalysisHistoryUseCase(repository)


def get_detail_use_case(repository: RepositoryDep) -> GetAnalysisDetailUseCase:
    return GetAnalysisDetailUseCase(repository)


def get_dashboard_use_case(repository: RepositoryDep) -> GetDashboardSummaryUseCase:
    return GetDashboardSummaryUseCase(repository)


def get_delete_use_case(
    repository: RepositoryDep, storage: StorageDep
) -> DeleteAnalysisUseCase:
    return DeleteAnalysisUseCase(repository, storage)


UploadUseCaseDep = Annotated[UploadExamImageUseCase, Depends(get_upload_use_case)]
ListUseCaseDep = Annotated[ListAnalysisHistoryUseCase, Depends(get_list_use_case)]
DetailUseCaseDep = Annotated[GetAnalysisDetailUseCase, Depends(get_detail_use_case)]
DashboardUseCaseDep = Annotated[
    GetDashboardSummaryUseCase, Depends(get_dashboard_use_case)
]
DeleteUseCaseDep = Annotated[DeleteAnalysisUseCase, Depends(get_delete_use_case)]
