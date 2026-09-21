from dataclasses import dataclass

from src.api.schemas import TeacherResponse
from src.application.common.mediator import Query, RequestHandler
from src.domain.repositories.teacher_repository import TeacherRepository


@dataclass(frozen=True)
class GetTeachersQuery(Query[list[TeacherResponse]]):
    pass


class GetTeachersHandler(RequestHandler[GetTeachersQuery, list[TeacherResponse]]):
    def __init__(self, teacher_repository: TeacherRepository):
        self.teacher_repository = teacher_repository

    def handle(self, query: GetTeachersQuery) -> list[TeacherResponse]:
        return [
            TeacherResponse(id=t.id, name=t.name, department=t.department)
            for t in self.teacher_repository.get_all()
        ]
