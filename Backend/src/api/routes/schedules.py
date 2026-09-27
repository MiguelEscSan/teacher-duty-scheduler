from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_mediator
from src.api.schemas import SlotStatusUpdateRequest, SlotToggleRequest
from src.application.common.mediator import Mediator
from src.application.schedules.commands.assign_slot_group import AssignSlotGroupCommand
from src.application.schedules.commands.update_slot_status import ToggleSlotTypeCommand
from src.application.schedules.queries.get_teacher_base_schedule import GetTeacherBaseScheduleQuery

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
