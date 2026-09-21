from fastapi import APIRouter, Depends, HTTPException
from src.api.dependencies import get_guard_service
from src.api.schemas import OptimizeRequest
from src.services.guard_service import GuardService

router = APIRouter(prefix="/api/v1/guards", tags=["Guards Optimization"])


@router.post("/optimize")
def optimize_guards(payload: OptimizeRequest, service: GuardService = Depends(get_guard_service)):
    result = service.calculate_week(payload.start_date)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result