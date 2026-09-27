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
