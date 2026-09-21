from abc import ABC, abstractmethod

from src.domain.schedule import ScheduleEntry


class ScheduleRepository(ABC):
    """Port for weekly teacher schedules and duty lists."""

    @abstractmethod
    def get_for_teacher(self, teacher_id: str) -> list[ScheduleEntry]:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> list[ScheduleEntry]:
        raise NotImplementedError

    @abstractmethod
    def get_slot(
        self, teacher_id: str, day_of_week: int, period: int
    ) -> ScheduleEntry | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, entry: ScheduleEntry) -> ScheduleEntry:
        raise NotImplementedError

    @abstractmethod
    def delete_for_teacher(self, teacher_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_fixed_duty_teacher_ids(self, day_of_week: int, period: int) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_short_term_teacher_ids(self, day_of_week: int, period: int) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def delete_duties_for_teacher(self, teacher_id: str) -> None:
        raise NotImplementedError
