from dataclasses import dataclass
from datetime import datetime

from src.api.schemas import AvailableTeacherOut
from src.application.common.mediator import Query, RequestHandler
from src.domain.ports.absence_repository import AbsenceRepository
from src.domain.ports.schedule_repository import ScheduleRepository
from src.domain.repositories import SubstitutionRepository
from src.domain.ports.teacher_repository import TeacherRepository


@dataclass(frozen=True)
class GetAvailableCandidatesQuery(Query[list[AvailableTeacherOut]]):
    date_str: str
    period: int


class GetAvailableCandidatesHandler(
    RequestHandler[GetAvailableCandidatesQuery, list[AvailableTeacherOut]]
):
    def __init__(
        self,
        teacher_repository: TeacherRepository,
        absence_repository: AbsenceRepository,
        schedule_repository: ScheduleRepository,
        substitution_repository: SubstitutionRepository,
    ):
        self.teacher_repository = teacher_repository
        self.absence_repository = absence_repository
        self.schedule_repository = schedule_repository
        self.substitution_repository = substitution_repository

    def handle(self, request: GetAvailableCandidatesQuery) -> list[AvailableTeacherOut]:
        day = datetime.strptime(request.date_str, "%Y-%m-%d").weekday()
        if day > 4:
            return []
        absent_ids = {
            item.teacher_id for item in self.absence_repository.get_all(date=request.date_str)
            if item.period == request.period
        }
        busy_ids = self.substitution_repository.get_busy_teacher_ids(
            request.date_str, request.period
        )
        teaching_ids = {
            item.teacher_id for item in self.schedule_repository.get_all()
            if item.day_of_week == day and item.period == request.period and item.is_teaching
        }
        unavailable = absent_ids | busy_ids | teaching_ids
        fixed = set(self.schedule_repository.get_fixed_duty_teacher_ids(day, request.period))
        short = set(self.schedule_repository.get_short_term_teacher_ids(day, request.period))
        counts = self.substitution_repository.get_intervention_counts()
        priority = {"FIXED_DUTY": 0, "SHORT_TERM": 1, "FREE": 2}
        candidates = []
        for teacher in self.teacher_repository.get_all():
            if teacher.id in unavailable:
                continue
            duty_type = "FIXED_DUTY" if teacher.id in fixed else "SHORT_TERM" if teacher.id in short else "FREE"
            candidates.append(
                AvailableTeacherOut(
                    id=teacher.id, name=teacher.name, department=teacher.department,
                    duty_type=duty_type, interventions_count=counts.get(teacher.id, 0),
                )
            )
        return sorted(candidates, key=lambda item: (
            priority[item.duty_type], item.interventions_count, item.name.lower()
        ))
