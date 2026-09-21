# src/api/routes/absences.py
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.dependencies import get_mediator
from src.api.schemas import AbsenceCreate, AbsenceResponse
from src.application.absences.commands.create_absence import CreateAbsenceCommand
from src.application.absences.commands.delete_absence import DeleteAbsenceCommand
from src.application.absences.queries.get_actionable_absences import GetActionableAbsencesQuery
from src.application.common.mediator import Mediator


router = APIRouter(prefix="/api/v1/absences", tags=["Ausencias"])


@router.get("", response_model=list[AbsenceResponse])
def get_actionable_absences(mediator: Mediator = Depends(get_mediator)):
    """Devuelve las ausencias que requieren sustitución en aula."""
    return mediator.send(GetActionableAbsencesQuery())


@router.post("", status_code=status.HTTP_201_CREATED)
def create_absence(dto: AbsenceCreate, mediator: Mediator = Depends(get_mediator)):
    try:
        cmd = CreateAbsenceCommand(
            teacher_id=dto.teacher_id,
            date=dto.date,
            all_day=dto.all_day,
            period=dto.period,
            reason=dto.reason,
        )
        return mediator.send(cmd)
    except ValueError as ex:
        detail = str(ex)
        code = status.HTTP_404_NOT_FOUND if "no encontrado" in detail else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=detail)


@router.delete("/{absence_id}")
def delete_absence(absence_id: str, mediator: Mediator = Depends(get_mediator)):
    success = mediator.send(DeleteAbsenceCommand(absence_id=absence_id))
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ausencia no encontrada.")
    return {"message": "Ausencia eliminada con éxito."}