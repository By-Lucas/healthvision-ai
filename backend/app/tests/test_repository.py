"""Repository contract test.

Exercises the in-memory adapter against the AnalysisRepository port. Because the
SqlAlchemy adapter implements the same port, this documents the behavior every
repository must honor (filtering, summary aggregation, update semantics).
"""
import pytest

from app.domain.entities.analysis import Analysis, AnalysisStatus
from app.domain.value_objects.prediction import PredictedClass, Prediction
from app.tests.fakes import InMemoryAnalysisRepository


def _analysis(name: str) -> Analysis:
    return Analysis(
        original_filename=name,
        stored_filename=f"stored_{name}",
        image_path=f"/uploads/stored_{name}",
    )


@pytest.fixture
def repo() -> InMemoryAnalysisRepository:
    return InMemoryAnalysisRepository()


async def test_add_and_get(repo):
    a = await repo.add(_analysis("a.png"))
    fetched = await repo.get(a.id)
    assert fetched is not None
    assert fetched.original_filename == "a.png"


async def test_update_persists_completion(repo):
    a = await repo.add(_analysis("a.png"))
    a.complete(
        Prediction(
            predicted_class=PredictedClass.PNEUMONIA,
            confidence_score=0.91,
            processing_time_ms=12,
            class_probabilities={"NORMAL": 0.09, "PNEUMONIA": 0.91},
        )
    )
    await repo.update(a)
    fetched = await repo.get(a.id)
    assert fetched.status is AnalysisStatus.COMPLETED
    assert fetched.predicted_class is PredictedClass.PNEUMONIA


async def test_list_filters_by_status(repo):
    pending = await repo.add(_analysis("p.png"))
    done = await repo.add(_analysis("d.png"))
    done.complete(
        Prediction(PredictedClass.NORMAL, 0.8, 5, {"NORMAL": 0.8, "PNEUMONIA": 0.2})
    )
    await repo.update(done)

    only_pending = await repo.list(status=AnalysisStatus.PENDING)
    assert [a.id for a in only_pending] == [pending.id]


async def test_summary_aggregates(repo):
    a = await repo.add(_analysis("a.png"))
    a.complete(
        Prediction(PredictedClass.NORMAL, 0.6, 5, {"NORMAL": 0.6, "PNEUMONIA": 0.4})
    )
    await repo.update(a)
    summary = await repo.summary()
    assert summary.total_analyses == 1
    assert summary.by_class.get("NORMAL") == 1
    assert summary.average_confidence == 0.6
