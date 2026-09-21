from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas import OptimizeRequest
from src.api.dependencies import get_mediator
from src.application.common.mediator import Mediator
from src.application.guards.queries.calculate_week_guards import CalculateWeekGuardsQuery

router = APIRouter(prefix="/api/v1/guards", tags=["Guards Optimization"])


@router.post("/optimize")
def optimize_guards(
    payload: OptimizeRequest, mediator: Mediator = Depends(get_mediator)
):
    result = mediator.send(CalculateWeekGuardsQuery(start_date=payload.start_date))
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result