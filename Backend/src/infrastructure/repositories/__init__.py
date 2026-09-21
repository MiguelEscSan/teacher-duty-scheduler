"""SQLModel repository adapters.

Only this package knows about SQLModel and the persistence models.  The
application receives the domain repository ports from ``api.dependencies``.
"""

from src.infrastructure.repositories.absence_repository import SQLAbsenceRepository
from src.infrastructure.repositories.schedule_repository import SQLScheduleRepository
from src.infrastructure.repositories.student_group_repository import (
    SQLStudentGroupRepository,
)
from src.infrastructure.repositories.substitution_repository import (
    SQLSubstitutionRepository,
)
from src.infrastructure.repositories.teacher_repository import SQLTeacherRepository


class SQLGuardRepository:
    """Backward-compatible facade for the original guard repository.

    New code should inject the five focused repositories.  This facade remains
    available for integrations that used the pre-refactor API.
    """

    def __init__(self, session):
        self.teachers = SQLTeacherRepository(session)
        self.absences = SQLAbsenceRepository(session)
        self.schedules = SQLScheduleRepository(session)

    def get_all_teachers(self):
        return self.teachers.get_all()

    def get_teacher_by_id(self, teacher_id):
        return self.teachers.get_by_id(teacher_id)

    def save_teacher(self, teacher):
        return self.teachers.save(teacher)

    def delete_teacher(self, teacher_id):
        return self.teachers.delete(teacher_id)

    def get_base_schedule_for_teacher(self, teacher_id):
        return self.schedules.get_for_teacher(teacher_id)

    def get_all_base_schedules(self):
        return self.schedules.get_all()

    def toggle_base_slot(self, teacher_id, day, period):
        entry = self.schedules.get_slot(teacher_id, day, period)
        if entry:
            entry.is_teaching = entry.group_id is None
            self.schedules.save(entry)
            return "TEACHING" if entry.is_teaching else "FREE"
        self.schedules.save(
            self.schedules.entry_type(
                teacher_id=teacher_id,
                day_of_week=day,
                period=period,
                is_teaching=True,
            )
        )
        return "TEACHING"

    def get_all_absences(self):
        return self.absences.get_all()

    def get_absences_by_dates(self, dates):
        return self.absences.get_by_dates(dates)

    def create_absence(self, absence):
        return self.absences.save(absence)

    def delete_absence(self, absence_id: str):
        return self.absences.delete(absence_id)


__all__ = [
    "SQLAbsenceRepository",
    "SQLGuardRepository",
    "SQLScheduleRepository",
    "SQLStudentGroupRepository",
    "SQLSubstitutionRepository",
    "SQLTeacherRepository",
]
