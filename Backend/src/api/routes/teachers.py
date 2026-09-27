from fastapi import APIRouter, Depends, HTTPException, status
from src.api.dependencies import get_mediator
from src.api.schemas import (
    TeacherCreate,
    TeacherResponse,
    TeacherUpdate,
)
from src.application.common.mediator import Mediator
from src.application.teachers.commands.create_teacher import CreateTeacherCommand
from src.application.teachers.commands.delete_teacher import DeleteTeacherCommand
from src.application.teachers.commands.update_teacher import UpdateTeacherCommand
from src.application.teachers.queries.get_teachers import GetTeachersQuery

router = APIRouter(prefix="/api/v1/teachers", tags=["Teachers"])


@router.get("", response_model=list[TeacherResponse])
def list_teachers(mediator: Mediator = Depends(get_mediator)):
    return [TeacherResponse.model_validate(item) for item in mediator.send(GetTeachersQuery())]


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
    return TeacherResponse.model_validate(mediator.send(cmd))


@router.put("/{teacher_id}", response_model=TeacherResponse)
def update_teacher(
    teacher_id: str,
    dto: TeacherUpdate,
    mediator: Mediator = Depends(get_mediator),
):
    try:
        return TeacherResponse.model_validate(mediator.send(
            UpdateTeacherCommand(
                teacher_id=teacher_id,
                name=dto.name,
                department=dto.department,
                email=dto.email,
            )
        ))
    except EntityNotFoundException as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ex))
    except ValueError as ex:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex))


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