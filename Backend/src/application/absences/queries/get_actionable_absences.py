from datetime import datetime
from sqlmodel import Session, select
from src.application.common.mediator import RequestHandler
from src.infrastructure.db.models import AbsenceDB, StudentGroupDB, TeacherDB, TeacherScheduleDB
from dataclasses import dataclass
from src.api.schemas import AbsenceResponse
from src.application.common.mediator import Query


@dataclass(frozen=True)
class GetActionableAbsencesQuery(Query[list[AbsenceResponse]]):
    date: str | None = None
    teacher_id: str | None = None
    resolved: bool | None = None

class GetActionableAbsencesHandler(
    RequestHandler[GetActionableAbsencesQuery, list[AbsenceResponse]]
):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, query: GetActionableAbsencesQuery) -> list[AbsenceResponse]:
        absences_query = select(AbsenceDB)
        if query.date is not None:
            absences_query = absences_query.where(AbsenceDB.date == query.date)
        if query.teacher_id is not None:
            absences_query = absences_query.where(AbsenceDB.teacher_id == query.teacher_id)
        if query.resolved is not None:
            absences_query = absences_query.where(AbsenceDB.resolved == query.resolved)

        absences = self.session.exec(absences_query).all()
        teachers = {t.id: t.name for t in self.session.exec(select(TeacherDB)).all()}
        groups = {g.id: g for g in self.session.exec(select(StudentGroupDB)).all()}

        schedules = self.session.exec(
            select(TeacherScheduleDB).where(
                TeacherScheduleDB.is_teaching == True,
                TeacherScheduleDB.group_id.is_not(None),
            )
        ).all()
        teaching_map = {(s.teacher_id, s.day_of_week, s.period): s.group_id for s in schedules}

        results: list[AbsenceResponse] = []
        for a in absences:
            try:
                day_of_week = datetime.strptime(a.date, "%Y-%m-%d").weekday()
            except ValueError:
                continue

            group_id = teaching_map.get((a.teacher_id, day_of_week, a.period))
            if group_id:
                group_obj = groups.get(group_id)
                group_name = group_obj.name if group_obj else "Grupo asignado"
                student_count = group_obj.student_count if group_obj else None

                results.append(
                    AbsenceResponse(
                        id=a.id,
                        teacher_id=a.teacher_id,
                        teacher_name=teachers.get(a.teacher_id, a.teacher_id),
                        date=a.date,
                        period=a.period,
                        resolved=a.resolved,
                        group_id=group_id,
                        group_name=group_name,
                        student_count=student_count,
                        reason=a.reason,
                    )
                )

        results.sort(key=lambda x: (x.date, x.period))
        return results