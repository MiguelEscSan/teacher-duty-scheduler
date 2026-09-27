from dataclasses import dataclass

from src.application.common.mediator import Command, RequestHandler
from src.application.schedules.dtos.student_group_response import StudentGroupResponseDto
from src.domain.exceptions.assignment_exceptions import (
    ConflictException,
    EntityNotFoundException,
)
from src.domain.ports.student_group_repository import StudentGroupRepository


@dataclass(frozen=True)
class UpdateStudentGroupCommand(Command[StudentGroupResponseDto]):
    group_id: str
    name: str
    student_count: int | None = None


class UpdateStudentGroupHandler(
    RequestHandler[UpdateStudentGroupCommand, StudentGroupResponseDto]
):
    def __init__(self, student_group_repository: StudentGroupRepository):
        self.student_group_repository = student_group_repository

    def handle(self, cmd: UpdateStudentGroupCommand) -> StudentGroupResponseDto:
        group = self.student_group_repository.get_by_id(cmd.group_id)
        if group is None:
            raise EntityNotFoundException("Grupo de alumnos no encontrado.")

        clean_name = cmd.name.strip()
        if clean_name != group.name:
            existing = self.student_group_repository.get_by_name(clean_name)
            if existing is not None and existing.id != group.id:
                raise ConflictException(f"Ya existe un grupo con el nombre '{cmd.name}'.")

        group.update(name=cmd.name, student_count=cmd.student_count)
        self.student_group_repository.save(group)
        return StudentGroupResponseDto(
            id=group.id, name=group.name, student_count=group.student_count
        )
