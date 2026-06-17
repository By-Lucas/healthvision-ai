"""SQLAlchemy async implementation of the AnalysisRepository port.

Translates between the persistence model (`AnalysisModel`) and the domain
entity (`Analysis`). The rest of the app only sees domain entities.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.dashboard import DashboardSummary
from app.domain.entities.analysis import Analysis, AnalysisStatus
from app.domain.ports import AnalysisRepository
from app.domain.value_objects.prediction import PredictedClass
from app.infrastructure.database.models.analysis_model import AnalysisModel


def _to_entity(model: AnalysisModel) -> Analysis:
    return Analysis(
        id=model.id,
        original_filename=model.original_filename,
        stored_filename=model.stored_filename,
        image_path=model.image_path,
        status=AnalysisStatus(model.status),
        predicted_class=(
            PredictedClass(model.predicted_class) if model.predicted_class else None
        ),
        confidence_score=model.confidence_score,
        explanation=model.explanation,
        processing_time_ms=model.processing_time_ms,
        error_message=model.error_message,
        findings=model.findings,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _apply_entity(model: AnalysisModel, entity: Analysis) -> None:
    model.status = entity.status.value
    model.predicted_class = (
        entity.predicted_class.value if entity.predicted_class else None
    )
    model.confidence_score = entity.confidence_score
    model.explanation = entity.explanation
    model.processing_time_ms = entity.processing_time_ms
    model.error_message = entity.error_message
    model.findings = entity.findings


class SqlAlchemyAnalysisRepository(AnalysisRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, analysis: Analysis) -> Analysis:
        model = AnalysisModel(
            id=analysis.id,
            original_filename=analysis.original_filename,
            stored_filename=analysis.stored_filename,
            image_path=analysis.image_path,
            status=analysis.status.value,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def get(self, analysis_id: UUID) -> Analysis | None:
        model = await self._session.get(AnalysisModel, analysis_id)
        return _to_entity(model) if model else None

    async def update(self, analysis: Analysis) -> Analysis:
        model = await self._session.get(AnalysisModel, analysis.id)
        if model is None:
            raise ValueError(f"Analysis {analysis.id} does not exist")
        _apply_entity(model, analysis)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def delete(self, analysis_id: UUID) -> bool:
        model = await self._session.get(AnalysisModel, analysis_id)
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True

    async def list(
        self,
        *,
        status: AnalysisStatus | None = None,
        predicted_class: PredictedClass | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Analysis]:
        stmt = select(AnalysisModel).order_by(AnalysisModel.created_at.desc())
        if status is not None:
            stmt = stmt.where(AnalysisModel.status == status.value)
        if predicted_class is not None:
            stmt = stmt.where(AnalysisModel.predicted_class == predicted_class.value)
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [_to_entity(m) for m in result.scalars().all()]

    async def summary(self) -> DashboardSummary:
        total = await self._session.scalar(
            select(func.count()).select_from(AnalysisModel)
        )
        avg_conf = await self._session.scalar(
            select(func.avg(AnalysisModel.confidence_score)).where(
                AnalysisModel.confidence_score.is_not(None)
            )
        )

        by_class_rows = await self._session.execute(
            select(AnalysisModel.predicted_class, func.count())
            .where(AnalysisModel.predicted_class.is_not(None))
            .group_by(AnalysisModel.predicted_class)
        )
        by_status_rows = await self._session.execute(
            select(AnalysisModel.status, func.count()).group_by(AnalysisModel.status)
        )

        return DashboardSummary(
            total_analyses=int(total or 0),
            average_confidence=round(float(avg_conf or 0.0), 4),
            by_class={k: int(v) for k, v in by_class_rows.all() if k},
            by_status={k: int(v) for k, v in by_status_rows.all()},
        )
