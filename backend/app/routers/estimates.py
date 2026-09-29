from fastapi import APIRouter, Query
from app.schemas.estimate import EstimateRequest
from app.services import estimate_service
router = APIRouter()

@router.get("/estimate")
def get_est(
    box_ids: list[int] = Query(default=[]),
    box_id: int | None = Query(None),
    overlap: float | None = None,
    wrap_style: str = "cross",
    save: bool = False,
):
    return estimate_service.run_estimate(box_ids, overlap, wrap_style, save, "", box_id=box_id)

@router.post("/estimate")
def post_est(body: EstimateRequest):
    return estimate_service.run_estimate(
        body.box_ids, body.overlap, body.wrap_style, body.save, body.note, box_id=body.box_id
    )
