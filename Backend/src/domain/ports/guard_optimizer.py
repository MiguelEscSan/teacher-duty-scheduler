from abc import ABC, abstractmethod

from src.domain.guard import AssignmentReport
from src.domain.schedule import TeacherSchedule, TimeSlot
from src.domain.teacher import Teacher


class GuardOptimizer(ABC):
    @abstractmethod
    def generate_schedule(
        self,
        teachers: list[Teacher],
        slots: list[TimeSlot],
        schedules: dict[str, TeacherSchedule],
        time_limit_seconds: float = 6.0,
    ) -> AssignmentReport:
        raise NotImplementedError
