from dataclasses import dataclass

from src.api.schemas import TeacherResponse
from src.application.common.mediator import Command, RequestHandler
from src.domain.ports.teacher_repository import TeacherRepository
from src.domain.teacher import CorporateEmail, Teacher


@dataclass(frozen=True)
class CreateTeacherCommand(Command[TeacherResponse]):
    name: str
    department: str = "General"
    email: str | None = None


class CreateTeacherHandler(RequestHandler[CreateTeacherCommand, TeacherResponse]):
    def __init__(self, teacher_repository: TeacherRepository):
        self.teacher_repository = teacher_repository

    def handle(self, cmd: CreateTeacherCommand) -> TeacherResponse:
        teacher = Teacher.create(
            name=cmd.name,
            department=cmd.department,
            email=cmd.email,
        )
        saved = self.teacher_repository.save(teacher)
        return TeacherResponse(
            id=saved.id,
            name=saved.name,
            department=saved.department,
            email=saved.email.email if saved.email else None,
        )
