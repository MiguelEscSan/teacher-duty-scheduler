from dataclasses import dataclass
from typing import Any

from src.application.common.mediator import Query, RequestHandler
from src.domain.ports.schedule_repository import ScheduleRepository
from src.domain.ports.student_group_repository import StudentGroupRepository
from src.domain.ports.teacher_repository import TeacherRepository


@dataclass(frozen=True)
class GetTeacherBaseScheduleQuery(Query[list[list[dict[str, Any]]]]):
    teacher_id: str


class GetTeacherBaseScheduleHandler(
    RequestHandler[GetTeacherBaseScheduleQuery, list[list[dict[str, Any]]]]
):
    def __init__(
        self,
        schedule_repository: ScheduleRepository,
        student_group_repository: StudentGroupRepository,
        teacher_repository: TeacherRepository,
    ):
        self.schedule_repository = schedule_repository
        self.student_group_repository = student_group_repository
        self.teacher_repository = teacher_repository

    def handle(self, query: GetTeacherBaseScheduleQuery) -> list[list[dict[str, Any]]]:
        if not self.teacher_repository.get_by_id(query.teacher_id):
            raise ValueError("Profesor no encontrado.")
        entries = self.schedule_repository.get_for_teacher(query.teacher_id)
        groups = {g.id: g.name for g in self.student_group_repository.get_all()}
        slot_map = {}
        for entry in entries:
            slot_map[(entry.day_of_week, entry.period)] = {
                "status": "TEACHING" if entry.is_teaching and entry.group_id else "FREE",
                "group_id": entry.group_id if entry.is_teaching else None,
                "group_name": groups.get(entry.group_id) if entry.is_teaching else None,
            }
        return [
            [
                {
                    "day": day,
                    "period": period,
                    **slot_map.get(
                        (day, period),
                        {"status": "FREE", "group_id": None, "group_name": None},
                    ),
                }
                for day in range(5)
            ]
            for period in range(6)
        ]
