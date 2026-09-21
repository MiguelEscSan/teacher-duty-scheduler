from dataclasses import dataclass
from typing import Optional

from src.api.schemas import SubstitutionHistoryOut
from src.application.common.mediator import Query, RequestHandler
from src.domain.repositories.student_group_repository import StudentGroupRepository
from src.domain.repositories.substitution_repository import SubstitutionRepository
from src.domain.repositories.teacher_repository import TeacherRepository


@dataclass(frozen=True)
class GetSubstitutionHistoryQuery(Query[list[SubstitutionHistoryOut]]):
    date: Optional[str] = None
    substitute_teacher_id: Optional[str] = None
    absent_teacher_id: Optional[str] = None


class GetSubstitutionHistoryHandler(
    RequestHandler[GetSubstitutionHistoryQuery, list[SubstitutionHistoryOut]]
):
    def __init__(
        self,
        substitution_repository: SubstitutionRepository,
        teacher_repository: TeacherRepository,
        student_group_repository: StudentGroupRepository,
    ):
        self.substitution_repository = substitution_repository
        self.teacher_repository = teacher_repository
        self.student_group_repository = student_group_repository

    def handle(self, query: GetSubstitutionHistoryQuery) -> list[SubstitutionHistoryOut]:
        logs = self.substitution_repository.get_all(
            query.date, query.substitute_teacher_id, query.absent_teacher_id
        )
        teachers = {t.id: t.name for t in self.teacher_repository.get_all()}
        groups = {g.id: g.name for g in self.student_group_repository.get_all()}
        return [
            SubstitutionHistoryOut(
                id=int(log.id) if str(log.id).isdigit() else log.id,
                date=log.date,
                period=log.period,
                substitute_teacher_id=log.substitute_teacher_id,
                substitute_teacher_name=teachers.get(log.substitute_teacher_id, "Profesor no encontrado"),
                absent_teacher_id=log.absent_teacher_id,
                absent_teacher_name=teachers.get(log.absent_teacher_id, "Profesor no encontrado"),
                group_id=log.group_id,
                group_name=groups.get(log.group_id),
                source_type=log.source_type.value,
                created_at=log.created_at,
            )
            for log in logs
        ]
