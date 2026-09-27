from dataclasses import dataclass

from src.application.common.mediator import Query, RequestHandler
from src.application.teachers.dtos.teacher_response import TeacherResponseDto
from src.domain.ports.teacher_repository import TeacherRepository


@dataclass(frozen=True)
class GetTeachersQuery(Query[list[TeacherResponseDto]]):
    pass


class GetTeachersHandler(RequestHandler[GetTeachersQuery, list[TeacherResponseDto]]):
    def __init__(self, teacher_repository: TeacherRepository):
        self.teacher_repository = teacher_repository

    def handle(self, query: GetTeachersQuery) -> list[TeacherResponseDto]:
        return [
            TeacherResponseDto(
                id=t.id,
                name=t.name,
                department=t.department,
                email=t.email.email if t.email else None,
            )
            for t in self.teacher_repository.get_all()
        ]
