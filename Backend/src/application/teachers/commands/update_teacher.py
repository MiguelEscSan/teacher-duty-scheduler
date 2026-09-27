from dataclasses import dataclass

from src.api.schemas import TeacherResponse
from src.application.common.mediator import Command, RequestHandler
from src.domain.exceptions.assignment_exceptions import EntityNotFoundException
from src.domain.teacher import Teacher
from src.domain.ports.teacher_repository import TeacherRepository


@dataclass(frozen=True)
class UpdateTeacherCommand(Command[TeacherResponse]):
    teacher_id: str
    name: str
    department: str
    email: str | None = None


class UpdateTeacherHandler(RequestHandler[UpdateTeacherCommand, TeacherResponse]):
    def __init__(self, teacher_repository: TeacherRepository):
        self.teacher_repository = teacher_repository

    def handle(self, cmd: UpdateTeacherCommand) -> TeacherResponse:
        current = self.teacher_repository.get_by_id(cmd.teacher_id)
        if current is None:
            raise EntityNotFoundException("Profesor no encontrado.")

        updated = Teacher.create(
            name=cmd.name,
            department=cmd.department,
            email=cmd.email,
            teacher_id=current.id,
        )
        saved = self.teacher_repository.save(updated)
        return TeacherResponse(
            id=saved.id,
            name=saved.name,
            department=saved.department,
            email=saved.email.email if saved.email else None,
        )
