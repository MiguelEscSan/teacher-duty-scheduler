from dataclasses import dataclass
from src.api.schemas import TeacherResponse
from src.application.common.mediator import Query

from sqlmodel import Session, select
from src.api.schemas import TeacherResponse
from src.application.common.mediator import RequestHandler
from src.infrastructure.db.models import TeacherDB

@dataclass(frozen=True)
class GetTeachersQuery(Query[list[TeacherResponse]]):
    pass

class GetTeachersHandler(RequestHandler[GetTeachersQuery, list[TeacherResponse]]):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, query: GetTeachersQuery) -> list[TeacherResponse]:
        teachers = self.session.exec(select(TeacherDB)).all()
        return [
            TeacherResponse(
                id=t.id,
                name=t.name,
                department=t.department,
            )
            for t in teachers
        ]