"""Repository ports used by the application layer.

The interfaces in this package deliberately expose domain objects only.  SQL
models and transaction handling belong to the infrastructure adapters.
"""

from src.domain.ports.absence_repository import AbsenceRepository
from src.domain.ports.guard_optimizer import GuardOptimizer
from src.domain.ports.schedule_repository import ScheduleRepository
from src.domain.ports.student_group_repository import StudentGroupRepository
from src.domain.ports.substitution_repository import SubstitutionRepository
from src.domain.ports.teacher_repository import TeacherRepository

__all__ = [
    "AbsenceRepository",
    "GuardOptimizer",
    "ScheduleRepository",
    "StudentGroupRepository",
    "SubstitutionRepository",
    "TeacherRepository",
]
