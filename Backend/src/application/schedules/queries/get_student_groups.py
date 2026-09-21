from dataclasses import dataclass

from src.application.common.mediator import Query, RequestHandler
from src.domain.ports.student_group_repository import StudentGroupRepository


@dataclass(frozen=True)
class GetStudentGroupsQuery(Query[list]):
    pass


class GetStudentGroupsHandler(RequestHandler[GetStudentGroupsQuery, list]):
    def __init__(self, student_group_repository: StudentGroupRepository):
        self.student_group_repository = student_group_repository

    def handle(self, query: GetStudentGroupsQuery) -> list:
        return self.student_group_repository.get_all()
