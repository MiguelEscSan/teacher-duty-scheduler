from dataclasses import dataclass
from typing import Optional

from src.api.schemas import DutySlotOut, TeacherResponse
from src.application.common.mediator import Query, RequestHandler
from src.domain.constants import DAY_NAMES
from src.domain.repositories.schedule_repository import ScheduleRepository
from src.domain.repositories.teacher_repository import TeacherRepository


@dataclass(frozen=True)
class GetShortTermTeachersQuery(Query[list[DutySlotOut]]):
    day_of_week: Optional[int] = None
    period: Optional[int] = None


class GetShortTermTeachersHandler(RequestHandler[GetShortTermTeachersQuery, list[DutySlotOut]]):
    def __init__(self, schedule_repository: ScheduleRepository, teacher_repository: TeacherRepository):
        self.schedule_repository = schedule_repository
        self.teacher_repository = teacher_repository

    def handle(self, query: GetShortTermTeachersQuery) -> list[DutySlotOut]:
        days = [query.day_of_week] if query.day_of_week is not None else range(5)
        periods = [query.period] if query.period is not None else range(6)
        teachers = {t.id: t for t in self.teacher_repository.get_all()}
        by_slot: dict[tuple[int, int], list[TeacherResponse]] = {}
        for day in days:
            for period in periods:
                for teacher_id in self.schedule_repository.get_short_term_teacher_ids(day, period):
                    teacher = teachers.get(teacher_id)
                    if teacher:
                        by_slot.setdefault((day, period), []).append(
                            TeacherResponse(id=teacher.id, name=teacher.name, department=teacher.department)
                        )
        return [
            DutySlotOut(
                day_of_week=day,
                day_name=DAY_NAMES[day],
                period=period,
                teachers=sorted(by_slot.get((day, period), []), key=lambda t: t.name.lower()),
            )
            for day in days
            for period in periods
        ]
