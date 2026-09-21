from dataclasses import dataclass
from typing import Optional
from src.application.common.mediator import Query
from sqlmodel import Session, select
from src.api.schemas import SubstitutionHistoryOut
from src.application.common.mediator import RequestHandler
from src.infrastructure.db.models import StudentGroupDB, SubstitutionLogDB, TeacherDB

@dataclass(frozen=True)
class GetSubstitutionHistoryQuery(Query[list[SubstitutionHistoryOut]]):
    date: Optional[str] = None
    substitute_teacher_id: Optional[str] = None
    absent_teacher_id: Optional[str] = None

class GetSubstitutionHistoryHandler(
    RequestHandler[GetSubstitutionHistoryQuery, list[SubstitutionHistoryOut]]
):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, query: GetSubstitutionHistoryQuery) -> list[SubstitutionHistoryOut]:
        history_query = select(SubstitutionLogDB).order_by(
            SubstitutionLogDB.date.desc(),
            SubstitutionLogDB.period,
            SubstitutionLogDB.created_at.desc(),
        )
        if query.date is not None:
            history_query = history_query.where(SubstitutionLogDB.date == query.date)
        if query.substitute_teacher_id is not None:
            history_query = history_query.where(
                SubstitutionLogDB.substitute_teacher_id == query.substitute_teacher_id
            )
        if query.absent_teacher_id is not None:
            history_query = history_query.where(
                SubstitutionLogDB.absent_teacher_id == query.absent_teacher_id
            )

        logs = self.session.exec(history_query).all()
        if not logs:
            return []

        teacher_ids = {
            t_id
            for log in logs
            for t_id in (log.substitute_teacher_id, log.absent_teacher_id)
        }
        teachers = {
            t.id: t.name
            for t in self.session.exec(
                select(TeacherDB).where(TeacherDB.id.in_(teacher_ids))
            ).all()
        }

        group_ids = {log.group_id for log in logs if log.group_id is not None}
        groups = {
            g.id: g.name
            for g in self.session.exec(
                select(StudentGroupDB).where(StudentGroupDB.id.in_(group_ids))
            ).all()
        }

        return [
            SubstitutionHistoryOut(
                id=log.id,
                date=log.date,
                period=log.period,
                substitute_teacher_id=log.substitute_teacher_id,
                substitute_teacher_name=teachers.get(
                    log.substitute_teacher_id, "Profesor no encontrado"
                ),
                absent_teacher_id=log.absent_teacher_id,
                absent_teacher_name=teachers.get(
                    log.absent_teacher_id, "Profesor no encontrado"
                ),
                group_id=log.group_id,
                group_name=groups.get(log.group_id),
                source_type=(
                    log.source_type.value
                    if hasattr(log.source_type, "value")
                    else str(log.source_type)
                ),
                created_at=log.created_at,
            )
            for log in logs
        ]