from __future__ import annotations

from fastapi import APIRouter

from app.interfaces.api.dependencies import DashboardUseCaseDep, ListUseCaseDep
from app.interfaces.api.schemas.analysis_schema import AnalysisResponse
from app.interfaces.api.schemas.dashboard_schema import DashboardSummaryResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
async def dashboard_summary(
    dashboard_use_case: DashboardUseCaseDep,
    list_use_case: ListUseCaseDep,
) -> DashboardSummaryResponse:
    summary = await dashboard_use_case.execute()
    recent = await list_use_case.execute(limit=5, offset=0)
    return DashboardSummaryResponse.from_dto(
        summary, [AnalysisResponse.from_entity(a) for a in recent]
    )
