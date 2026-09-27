from dataclasses import dataclass

from src.application.common.mediator import Query, RequestHandler
from src.application.schedules.dtos.student_group_response import StudentGroupResponseDto
from src.domain.ports.student_group_repository import StudentGroupRepository


@dataclass(frozen=True)
class GetStudentGroupsQuery(Query[list[StudentGroupResponseDto]]):
    pass


class GetStudentGroupsHandler(
    RequestHandler[GetStudentGroupsQuery, list[StudentGroupResponseDto]]
):
    def __init__(self, student_group_repository: StudentGroupRepository):
        self.student_group_repository = student_group_repository

    def handle(self, query: GetStudentGroupsQuery) -> list[StudentGroupResponseDto]:
        return [
            StudentGroupResponseDto(
                id=group.id,
                name=group.name,
                student_count=group.student_count,
            )
            for group in self.student_group_repository.get_all()
        ]
