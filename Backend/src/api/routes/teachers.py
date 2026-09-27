from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.api.dependencies import get_mediator
from src.api.schemas import (
    DutyAssignmentRequest,
    DutyAssignmentResponse,
    DutySlotOut,
    TeacherCreate,
    TeacherResponse,
)
from src.application.common.mediator import Mediator
from src.application.teachers.commands.create_teacher import CreateTeacherCommand
from src.application.teachers.commands.delete_teacher import DeleteTeacherCommand
from src.application.teachers.commands.manage_duty_assignment import AssignTeacherDutyCommand
from src.application.teachers.commands.remove_duty_assignment import RemoveTeacherDutyCommand
from src.application.teachers.queries.get_duty_teachers import GetDutyTeachersQuery
from src.application.teachers.queries.get_short_term_teachers import GetShortTermTeachersQuery
from src.application.teachers.queries.get_teachers import GetTeachersQuery
from src.domain.exceptions.assignment_exceptions import EntityNotFoundException
from src.domain.exceptions.invalid_operation_exception import InvalidOperationException

router = APIRouter(prefix="/api/v1/teachers", tags=["Teachers"])


@router.get("", response_model=list[TeacherResponse])
def list_teachers(mediator: Mediator = Depends(get_mediator)):
    return mediator.send(GetTeachersQuery())


@router.post("", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(
    dto: TeacherCreate,
    mediator: Mediator = Depends(get_mediator),
):
    cmd = CreateTeacherCommand(
        name=dto.name,
        department=dto.department,
        email=dto.email,
    )
    return mediator.send(cmd)


@router.get("/duty", response_model=List[DutySlotOut])
def get_duty_teachers(
    day_of_week: int | None = Query(default=None, ge=0, le=4),
    period: int | None = Query(default=None, ge=0, le=5),
    mediator: Mediator = Depends(get_mediator),
):
    return mediator.send(GetDutyTeachersQuery(day_of_week=day_of_week, period=period))


@router.get("/short-term", response_model=List[DutySlotOut])
def get_short_term_teachers(
    day_of_week: int | None = Query(default=None, ge=0, le=4),
    period: int | None = Query(default=None, ge=0, le=5),
    mediator: Mediator = Depends(get_mediator),
):
    return mediator.send(
        GetShortTermTeachersQuery(day_of_week=day_of_week, period=period)
    )


@router.post("/duty-assignment", response_model=DutyAssignmentResponse)
def assign_teacher_duty(
    payload: DutyAssignmentRequest, mediator: Mediator = Depends(get_mediator)
):
    try:
        return mediator.send(AssignTeacherDutyCommand(
            teacher_id=payload.teacher_id,
            day_of_week=payload.day_of_week,
            period=payload.period,
            duty_type=payload.duty_type,
        ))
    except ValueError as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ex))
    except InvalidOperationException as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))


@router.delete("/duty-assignment", response_model=DutyAssignmentResponse)
def remove_teacher_duty(
    payload: DutyAssignmentRequest, mediator: Mediator = Depends(get_mediator)
):
    try:
        return mediator.send(RemoveTeacherDutyCommand(
            teacher_id=payload.teacher_id,
            day_of_week=payload.day_of_week,
            period=payload.period,
            duty_type=payload.duty_type,
        ))
    except (ValueError, EntityNotFoundException) as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ex))
    except InvalidOperationException as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))


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