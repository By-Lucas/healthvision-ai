"""Pytest fixtures.

Builds the FastAPI app with the persistence/storage/queue adapters swapped for
in-memory fakes via dependency overrides. No external services required.
"""
from __future__ import annotations

import os
import tempfile

# Point storage at a writable temp dir BEFORE the app/config is imported,
# so the default container path (/data) is never touched during tests.
os.environ.setdefault("STORAGE_DIR", tempfile.mkdtemp(prefix="hv-test-"))

import io  # noqa: E402

import numpy as np  # noqa: E402
import pytest  # noqa: E402
from PIL import Image  # noqa: E402

from app.interfaces.api import dependencies as deps
from app.main import app
from app.tests.fakes import InMemoryAnalysisRepository, InMemoryStorage


@pytest.fixture
def repository() -> InMemoryAnalysisRepository:
    return InMemoryAnalysisRepository()


@pytest.fixture
def storage() -> InMemoryStorage:
    return InMemoryStorage()


@pytest.fixture
def client(repository, storage):
    from fastapi.testclient import TestClient

    from app.application.use_cases.delete_analysis import DeleteAnalysisUseCase
    from app.application.use_cases.get_analysis_detail import (
        GetAnalysisDetailUseCase,
    )
    from app.application.use_cases.get_dashboard_summary import (
        GetDashboardSummaryUseCase,
    )
    from app.application.use_cases.list_analysis_history import (
        ListAnalysisHistoryUseCase,
    )
    from app.application.use_cases.upload_exam_image import (
        UploadExamImageUseCase,
    )

    validator = deps.get_validator()

    app.dependency_overrides[deps.get_upload_use_case] = lambda: UploadExamImageUseCase(
        repository=repository,
        storage=storage,
        validator=validator,
        enqueue_analysis=lambda _id: None,  # do not hit a real broker in tests
    )
    app.dependency_overrides[deps.get_list_use_case] = (
        lambda: ListAnalysisHistoryUseCase(repository)
    )
    app.dependency_overrides[deps.get_detail_use_case] = (
        lambda: GetAnalysisDetailUseCase(repository)
    )
    app.dependency_overrides[deps.get_dashboard_use_case] = (
        lambda: GetDashboardSummaryUseCase(repository)
    )
    app.dependency_overrides[deps.get_delete_use_case] = (
        lambda: DeleteAnalysisUseCase(repository, storage)
    )

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def make_png_bytes(brightness: int = 200, size: int = 64) -> bytes:
    arr = np.full((size, size, 3), brightness, dtype=np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    return buf.getvalue()
