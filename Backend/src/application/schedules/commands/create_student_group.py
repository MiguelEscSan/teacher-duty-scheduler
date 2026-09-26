from dataclasses import dataclass

from src.api.schemas import StudentGroupResponseDto
from src.application.common.mediator import Command, RequestHandler
from src.domain.exceptions.assignment_exceptions import ConflictException
from src.domain.ports.student_group_repository import StudentGroupRepository
from src.domain.student_group import StudentGroup


@dataclass(frozen=True)
class CreateStudentGroupCommand(Command[StudentGroupResponseDto]):
    name: str
    student_count: int | None = None


class CreateStudentGroupHandler(
    RequestHandler[CreateStudentGroupCommand, StudentGroupResponseDto]
):
    def __init__(self, student_group_repository: StudentGroupRepository):
        self.student_group_repository = student_group_repository

    def handle(self, cmd: CreateStudentGroupCommand) -> StudentGroupResponseDto:
        clean_name = cmd.name.strip()
        if self.student_group_repository.get_by_name(clean_name):
            raise ConflictException(f"Ya existe un grupo con el nombre '{cmd.name}'.")
        group = StudentGroup.create(
            name=cmd.name, student_count=cmd.student_count
        )
        self.student_group_repository.save(group)
        return StudentGroupResponseDto(
            id=group.id, name=group.name, student_count=group.student_count
        )
