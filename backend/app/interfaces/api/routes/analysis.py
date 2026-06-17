from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, File, Query, Response, UploadFile, status

from app.application.use_cases.upload_exam_image import UploadExamImageInput
from app.domain.entities.analysis import AnalysisStatus
from app.domain.value_objects.prediction import PredictedClass
from app.interfaces.api.dependencies import (
    DeleteUseCaseDep,
    DetailUseCaseDep,
    ListUseCaseDep,
    UploadUseCaseDep,
)
from app.interfaces.api.schemas.analysis_schema import (
    AnalysisListResponse,
    AnalysisResponse,
)

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post(
    "/upload",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a chest X-ray image for analysis",
)
async def upload_analysis(
    use_case: UploadUseCaseDep,
    file: UploadFile = File(...),
) -> AnalysisResponse:
    data = await file.read()
    analysis = await use_case.execute(
        UploadExamImageInput(
            filename=file.filename or "upload.jpg",
            content_type=file.content_type,
            data=data,
        )
    )
    return AnalysisResponse.from_entity(analysis)


@router.get("", response_model=AnalysisListResponse, summary="List analyses")
async def list_analyses(
    use_case: ListUseCaseDep,
    status_filter: AnalysisStatus | None = Query(default=None, alias="status"),
    predicted_class: PredictedClass | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> AnalysisListResponse:
    analyses = await use_case.execute(
        status=status_filter,
        predicted_class=predicted_class,
        limit=limit,
        offset=offset,
    )
    items = [AnalysisResponse.from_entity(a) for a in analyses]
    return AnalysisListResponse(items=items, count=len(items))


@router.get("/{analysis_id}", response_model=AnalysisResponse, summary="Get detail")
async def get_analysis(
    analysis_id: UUID, use_case: DetailUseCaseDep
) -> AnalysisResponse:
    analysis = await use_case.execute(analysis_id)
    return AnalysisResponse.from_entity(analysis)


@router.delete(
    "/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an analysis and its image",
)
async def delete_analysis(
    analysis_id: UUID, use_case: DeleteUseCaseDep
) -> Response:
    await use_case.execute(analysis_id)
    # Return an explicit empty Response so FastAPI doesn't attach a body to 204.
    return Response(status_code=status.HTTP_204_NO_CONTENT)
