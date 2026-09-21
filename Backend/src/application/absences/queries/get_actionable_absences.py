from dataclasses import dataclass
from datetime import datetime

from src.api.schemas import AbsenceResponse
from src.application.common.mediator import Query, RequestHandler
from src.domain.repositories.absence_repository import AbsenceRepository
from src.domain.repositories.schedule_repository import ScheduleRepository
from src.domain.repositories.student_group_repository import StudentGroupRepository
from src.domain.repositories.teacher_repository import TeacherRepository


@dataclass(frozen=True)
class GetActionableAbsencesQuery(Query[list[AbsenceResponse]]):
    date: str | None = None
    teacher_id: str | None = None
    resolved: bool | None = None


class GetActionableAbsencesHandler(RequestHandler[GetActionableAbsencesQuery, list[AbsenceResponse]]):
    def __init__(
        self,
        absence_repository: AbsenceRepository,
        teacher_repository: TeacherRepository,
        student_group_repository: StudentGroupRepository,
        schedule_repository: ScheduleRepository,
    ):
        self.absence_repository = absence_repository
        self.teacher_repository = teacher_repository
        self.student_group_repository = student_group_repository
        self.schedule_repository = schedule_repository

    def handle(self, query: GetActionableAbsencesQuery) -> list[AbsenceResponse]:
        absences = self.absence_repository.get_all(query.date, query.teacher_id, query.resolved)
        teachers = {t.id: t.name for t in self.teacher_repository.get_all()}
        groups = {g.id: g for g in self.student_group_repository.get_all()}
        schedules = [
            s for s in self.schedule_repository.get_all()
            if s.is_teaching and s.group_id is not None
        ]
        teaching_map = {(s.teacher_id, s.day_of_week, s.period): s.group_id for s in schedules}
        result = []
        for absence in absences:
            try:
                day = datetime.strptime(absence.date, "%Y-%m-%d").weekday()
            except ValueError:
                continue
            group_id = teaching_map.get((absence.teacher_id, day, absence.period))
            if not group_id:
                continue
            group = groups.get(group_id)
            result.append(
                AbsenceResponse(
                    id=absence.id,
                    teacher_id=absence.teacher_id,
                    teacher_name=teachers.get(absence.teacher_id, absence.teacher_id),
                    date=absence.date,
                    period=absence.period,
                    resolved=absence.resolved,
                    group_id=group_id,
                    group_name=group.name if group else "Grupo asignado",
                    student_count=group.student_count if group else None,
                    reason=absence.reason,
                )
            )
        return sorted(result, key=lambda item: (item.date, item.period))
