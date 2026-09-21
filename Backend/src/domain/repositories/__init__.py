"""Repository ports used by the application layer.

The interfaces in this package deliberately expose domain objects only.  SQL
models and transaction handling belong to the infrastructure adapters.
"""

from src.domain.repositories.absence_repository import AbsenceRepository
from src.domain.repositories.schedule_repository import ScheduleRepository
from src.domain.repositories.student_group_repository import StudentGroupRepository
from src.domain.repositories.substitution_repository import SubstitutionRepository
from src.domain.repositories.teacher_repository import TeacherRepository

__all__ = [
    "AbsenceRepository",
    "ScheduleRepository",
    "StudentGroupRepository",
    "SubstitutionRepository",
    "TeacherRepository",
]
