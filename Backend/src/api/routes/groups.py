from fastapi import APIRouter, Depends, Response, status

from src.api.dependencies import get_mediator
from src.api.schemas import (
    StudentGroupCreate,
    StudentGroupResponse,
    StudentGroupUpdate,
)
from src.application.common.mediator import Mediator
from src.application.schedules.commands.create_student_group import (
    CreateStudentGroupCommand,
)
from src.application.schedules.commands.delete_student_group import (
    DeleteStudentGroupCommand,
)
from src.application.schedules.commands.update_student_group import (
    UpdateStudentGroupCommand,
)
from src.application.schedules.queries.get_student_groups import GetStudentGroupsQuery

router = APIRouter(prefix="/api/v1/base-schedule/groups", tags=["Student Groups"])


@router.get("", response_model=list[StudentGroupResponse])
def get_student_groups(mediator: Mediator = Depends(get_mediator)):
    return mediator.send(GetStudentGroupsQuery())


@router.post("", response_model=StudentGroupResponse, status_code=status.HTTP_201_CREATED)
def create_student_group(
    payload: StudentGroupCreate, mediator: Mediator = Depends(get_mediator)
):
    return mediator.send(
        CreateStudentGroupCommand(
            name=payload.name, student_count=payload.student_count
        )
    )


@router.put("/{group_id}", response_model=StudentGroupResponse)
def update_student_group(
    group_id: str,
    payload: StudentGroupUpdate,
    mediator: Mediator = Depends(get_mediator),
):
    return mediator.send(
        UpdateStudentGroupCommand(
            group_id=group_id,
            name=payload.name,
            student_count=payload.student_count,
        )
    )


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student_group(
    group_id: str, mediator: Mediator = Depends(get_mediator)
):
    mediator.send(DeleteStudentGroupCommand(group_id=group_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
