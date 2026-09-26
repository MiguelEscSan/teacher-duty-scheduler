from abc import ABC, abstractmethod

from src.domain.teacher import Teacher


class TeacherRepository(ABC):
    """Port for persistence and lookup of teachers."""

    @abstractmethod
    def get_all(self) -> list[Teacher]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, teacher_id: str) -> Teacher | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, teacher: Teacher) -> Teacher:
        raise NotImplementedError

    @abstractmethod
    def delete(self, teacher_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def add_fixed_duty(self, teacher_id: str, day_of_week: int, period: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_fixed_duty(self, teacher_id: str, day_of_week: int, period: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def add_short_term_duty(self, teacher_id: str, day_of_week: int, period: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_short_term_duty(self, teacher_id: str, day_of_week: int, period: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_teacher_in_fixed_duty(
        self, teacher_id: str, day_of_week: int, period: int
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_teacher_in_short_term_duty(
        self, teacher_id: str, day_of_week: int, period: int
    ) -> bool:
        raise NotImplementedError
