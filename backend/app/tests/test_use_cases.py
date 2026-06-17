import pytest

from app.application.use_cases.process_exam_analysis import (
    ProcessExamAnalysisUseCase,
)
from app.application.use_cases.upload_exam_image import (
    UploadExamImageInput,
    UploadExamImageUseCase,
)
from app.core.exceptions import UnsupportedFileTypeError
from app.domain.entities.analysis import AnalysisStatus
from app.infrastructure.ai.predictor import MockInferenceEngine
from app.interfaces.api.dependencies import get_validator
from app.tests.conftest import make_png_bytes
from app.tests.fakes import InMemoryAnalysisRepository, InMemoryStorage


@pytest.fixture
def context():
    repo = InMemoryAnalysisRepository()
    storage = InMemoryStorage()
    validator = get_validator()
    return repo, storage, validator


async def test_upload_use_case_enqueues_and_persists(context):
    repo, storage, validator = context
    enqueued: list = []
    use_case = UploadExamImageUseCase(
        repository=repo,
        storage=storage,
        validator=validator,
        enqueue_analysis=lambda aid: enqueued.append(aid),
    )

    analysis = await use_case.execute(
        UploadExamImageInput("scan.png", "image/png", make_png_bytes())
    )

    assert analysis.status is AnalysisStatus.PENDING
    assert enqueued == [analysis.id]
    assert storage.exists(analysis.stored_filename)


async def test_upload_use_case_rejects_bad_type(context):
    repo, storage, validator = context
    use_case = UploadExamImageUseCase(repo, storage, validator, lambda _: None)
    with pytest.raises(UnsupportedFileTypeError):
        await use_case.execute(
            UploadExamImageInput("a.gif", "image/gif", make_png_bytes())
        )


async def test_process_use_case_completes_analysis(context):
    repo, storage, validator = context
    upload = UploadExamImageUseCase(repo, storage, validator, lambda _: None)
    analysis = await upload.execute(
        UploadExamImageInput("scan.png", "image/png", make_png_bytes())
    )

    process = ProcessExamAnalysisUseCase(repo, storage, MockInferenceEngine())
    await process.execute(analysis.id)

    updated = await repo.get(analysis.id)
    assert updated.status is AnalysisStatus.COMPLETED
    assert updated.predicted_class is not None
    assert 0.0 <= updated.confidence_score <= 1.0
    assert updated.processing_time_ms >= 1
    assert updated.explanation
    assert updated.findings  # populated (mock mirrors class probabilities)
