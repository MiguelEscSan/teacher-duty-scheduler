from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from src.api.dependencies import get_mediator
from src.api.schemas import TeacherCreate, TeacherResponse, DutySlotOut
from src.application.common.mediator import Query, Mediator
from src.application.teachers.commands.create_teacher import CreateTeacherCommand
from src.application.teachers.commands.delete_teacher import DeleteTeacherCommand
from src.application.teachers.queries.get_duty_teachers import GetDutyTeachersQuery
from src.application.teachers.queries.get_short_term_teachers import GetShortTermTeachersQuery
from src.application.teachers.queries.get_teachers import GetTeachersQuery

router = APIRouter(prefix="/api/teachers", tags=["Teachers"])


@router.get("", response_model=list[TeacherResponse])
def list_teachers(mediator: Mediator = Depends(get_mediator)):
    return mediator.send(GetTeachersQuery())


@router.post("", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(
    dto: TeacherCreate,
    mediator: Mediator = Depends(get_mediator),
):
    cmd = CreateTeacherCommand(name=dto.name, department=dto.department)
    return mediator.send(cmd)


@router.delete("/{teacher_id}")
def delete_teacher(
    teacher_id: str,
    mediator: Mediator = Depends(get_mediator),
):
    success = mediator.send(DeleteTeacherCommand(teacher_id=teacher_id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profesor no encontrado.",
        )
    return {"message": "Profesor eliminado"}

@router.get("/duty-teachers", response_model=List[DutySlotOut])
def get_duty_teachers(
    day_of_week: int | None = Query(default=None, ge=0, le=4),
    period: int | None = Query(default=None, ge=0, le=5),
    mediator: Mediator = Depends(get_mediator),
):
    return mediator.send(GetDutyTeachersQuery(day_of_week=day_of_week, period=period))


@router.get("/short-term-teachers", response_model=List[DutySlotOut])
def get_short_term_teachers(
    day_of_week: int | None = Query(default=None, ge=0, le=4),
    period: int | None = Query(default=None, ge=0, le=5),
    mediator: Mediator = Depends(get_mediator),
):
    return mediator.send(
        GetShortTermTeachersQuery(day_of_week=day_of_week, period=period)
    )