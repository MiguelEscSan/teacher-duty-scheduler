from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies import get_mediator
from src.api.schemas import (
    DutyAssignmentRequest,
    DutyAssignmentResponse,
    DutySlotOut,
    SlotStatusUpdateRequest,
    SlotToggleRequest,
)
from src.application.common.mediator import Mediator
from src.application.schedules.commands.assign_slot_group import AssignSlotGroupCommand
from src.application.schedules.commands.manage_duty_assignment import AssignTeacherDutyCommand
from src.application.schedules.commands.remove_duty_assignment import RemoveTeacherDutyCommand
from src.application.schedules.commands.update_slot_status import ToggleSlotTypeCommand
from src.application.schedules.queries.get_teacher_base_schedule import GetTeacherBaseScheduleQuery
from src.application.teachers.queries.get_duty_teachers import GetDutyTeachersQuery
from src.application.teachers.queries.get_short_term_teachers import GetShortTermTeachersQuery
from src.domain.exceptions.assignment_exceptions import EntityNotFoundException
from src.domain.exceptions.invalid_operation_exception import InvalidOperationException

router = APIRouter(prefix="/api/v1/base-schedule", tags=["Schedules & Absences"])


@router.get("/{teacher_id}")
def get_teacher_base_schedule(teacher_id: str, mediator: Mediator = Depends(get_mediator)):
    try:
        return mediator.send(GetTeacherBaseScheduleQuery(teacher_id=teacher_id))
    except ValueError as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.put("/assign-slot")
def assign_slot_group(payload: SlotToggleRequest, mediator: Mediator = Depends(get_mediator)):
    cmd = AssignSlotGroupCommand(
        teacher_id=payload.teacher_id,
        day=payload.day,
        period=payload.period,
        group_id=payload.group_id,
    )
    return mediator.send(cmd)


@router.put("/slot-status")
def update_slot_status(
    payload: SlotStatusUpdateRequest, mediator: Mediator = Depends(get_mediator)
):
    return mediator.send(
        ToggleSlotTypeCommand(
            teacher_id=payload.teacher_id,
            day=payload.day,
            period=payload.period,
            status=payload.status,
            group_id=payload.group_id,
        )
    )



@router.get("/duty", response_model=List[DutySlotOut])
def get_duty_teachers(
    day_of_week: int | None = Query(default=None, ge=0, le=4),
    period: int | None = Query(default=None, ge=0, le=5),
    mediator: Mediator = Depends(get_mediator),
):
    return [
        DutySlotOut.model_validate(item)
        for item in mediator.send(GetDutyTeachersQuery(day_of_week=day_of_week, period=period))
    ]


@router.get("/short-term", response_model=List[DutySlotOut])
def get_short_term_teachers(
    day_of_week: int | None = Query(default=None, ge=0, le=4),
    period: int | None = Query(default=None, ge=0, le=5),
    mediator: Mediator = Depends(get_mediator),
):
    return [
        DutySlotOut.model_validate(item)
        for item in mediator.send(
            GetShortTermTeachersQuery(day_of_week=day_of_week, period=period)
        )
    ]


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
