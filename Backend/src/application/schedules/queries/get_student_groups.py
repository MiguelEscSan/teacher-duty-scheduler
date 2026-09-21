from dataclasses import dataclass
from src.application.common.mediator import Query
from sqlmodel import Session, select
from src.application.common.mediator import RequestHandler
from src.infrastructure.db.models import StudentGroupDB

@dataclass(frozen=True)
class GetStudentGroupsQuery(Query[list[StudentGroupDB]]):
    pass

class GetStudentGroupsHandler(
    RequestHandler[GetStudentGroupsQuery, list[StudentGroupDB]]
):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, query: GetStudentGroupsQuery) -> list[StudentGroupDB]:
        return list(self.session.exec(select(StudentGroupDB)).all())