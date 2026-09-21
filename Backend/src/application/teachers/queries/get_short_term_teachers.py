from dataclasses import dataclass
from typing import Optional
from src.application.common.mediator import Query
from sqlmodel import Session, select
from src.api.schemas import DutySlotOut, TeacherResponse
from src.application.common.mediator import RequestHandler
from src.domain.constants import DAY_NAMES
from src.infrastructure.db.models import ShortTermSubstitutionDB, TeacherDB



@dataclass(frozen=True)
class GetShortTermTeachersQuery(Query[list[DutySlotOut]]):
    day_of_week: Optional[int] = None
    period: Optional[int] = None

class GetShortTermTeachersHandler(
    RequestHandler[GetShortTermTeachersQuery, list[DutySlotOut]]
):
    DAY_NAMES = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes")

    def __init__(self, session: Session):
        self.session = session

    def handle(self, query: GetShortTermTeachersQuery) -> list[DutySlotOut]:
        sub_query = select(ShortTermSubstitutionDB)
        if query.day_of_week is not None:
            sub_query = sub_query.where(
                ShortTermSubstitutionDB.day_of_week == query.day_of_week
            )
        if query.period is not None:
            sub_query = sub_query.where(ShortTermSubstitutionDB.period == query.period)

        substitutions = self.session.exec(sub_query).all()
        teacher_ids = {s.teacher_id for s in substitutions}
        teachers = {
            t.id: t
            for t in self.session.exec(
                select(TeacherDB).where(TeacherDB.id.in_(teacher_ids))
            ).all()
        }

        teachers_by_slot: dict[tuple[int, int], list[TeacherResponse]] = {}
        for sub in substitutions:
            teacher = teachers.get(sub.teacher_id)
            if teacher is None:
                continue

            teachers_by_slot.setdefault((sub.day_of_week, sub.period), []).append(
                TeacherResponse(
                    id=teacher.id,
                    name=teacher.name,
                    department=teacher.department,
                )
            )

        days = [query.day_of_week] if query.day_of_week is not None else range(5)
        periods = [query.period] if query.period is not None else range(6)

        return [
            DutySlotOut(
                day_of_week=d,
                day_name=DAY_NAMES[d],
                period=p,
                teachers=sorted(
                    teachers_by_slot.get((d, p), []),
                    key=lambda t: t.name.lower(),
                ),
            )
            for d in days
            for p in periods
        ]