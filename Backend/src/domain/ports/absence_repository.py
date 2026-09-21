from abc import ABC, abstractmethod

from src.domain.absence import Absence


class AbsenceRepository(ABC):
    """Port for absence persistence."""

    @abstractmethod
    def get_all(
        self,
        date: str | None = None,
        teacher_id: str | None = None,
        resolved: bool | None = None,
    ) -> list[Absence]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, absence_id: str) -> Absence | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_slot(self, teacher_id: str, date: str, period: int) -> Absence | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_dates(self, dates: list[str]) -> list[Absence]:
        raise NotImplementedError

    @abstractmethod
    def save(self, absence: Absence) -> Absence:
        raise NotImplementedError

    @abstractmethod
    def delete(self, absence_id: str) -> bool:
        raise NotImplementedError
