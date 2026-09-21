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


__all__ = [
    "SQLAbsenceRepository",
    "SQLScheduleRepository",
    "SQLStudentGroupRepository",
    "SQLSubstitutionRepository",
    "SQLTeacherRepository",
]
