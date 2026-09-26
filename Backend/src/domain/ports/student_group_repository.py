from abc import ABC, abstractmethod

from src.domain.student_group import StudentGroup


class StudentGroupRepository(ABC):
    """Port for the student-group catalogue."""

    @abstractmethod
    def get_all(self) -> list[StudentGroup]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, group_id: str) -> StudentGroup | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_name(self, name: str) -> StudentGroup | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, group: StudentGroup) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, group_id: str) -> None:
        raise NotImplementedError
