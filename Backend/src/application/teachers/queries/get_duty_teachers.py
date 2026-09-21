from dataclasses import dataclass
from typing import Optional
from src.application.common.mediator import Query

from sqlmodel import Session, select
from src.api.schemas import DutySlotOut, TeacherResponse
from src.application.common.mediator import RequestHandler
from src.domain.constants import DAY_NAMES
from src.infrastructure.db.models import FixedDutyDB, TeacherDB

@dataclass(frozen=True)
class GetDutyTeachersQuery(Query[list[DutySlotOut]]):
    day_of_week: Optional[int] = None
    period: Optional[int] = None



class GetDutyTeachersHandler(RequestHandler[GetDutyTeachersQuery, list[DutySlotOut]]):

    DAY_NAMES = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes")

    def __init__(self, session: Session):
        self.session = session

    def handle(self, query: GetDutyTeachersQuery) -> list[DutySlotOut]:
        duty_query = select(FixedDutyDB)
        if query.day_of_week is not None:
            duty_query = duty_query.where(FixedDutyDB.day_of_week == query.day_of_week)
        if query.period is not None:
            duty_query = duty_query.where(FixedDutyDB.period == query.period)

        duties = self.session.exec(duty_query).all()
        teacher_ids = {duty.teacher_id for duty in duties}
        teachers = {
            t.id: t
            for t in self.session.exec(
                select(TeacherDB).where(TeacherDB.id.in_(teacher_ids))
            ).all()
        }

        teachers_by_slot: dict[tuple[int, int], list[TeacherResponse]] = {}
        for duty in duties:
            teacher = teachers.get(duty.teacher_id)
            if teacher is None:
                continue

            teachers_by_slot.setdefault((duty.day_of_week, duty.period), []).append(
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