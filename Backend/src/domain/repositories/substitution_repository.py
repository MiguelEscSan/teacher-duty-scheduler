from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.substitution import SubstitutionLog


class SubstitutionRepository(ABC):
    """Port for substitution audit logs and rotation queries."""

    @abstractmethod
    def get_all(
        self,
        date: str | None = None,
        substitute_teacher_id: str | None = None,
        absent_teacher_id: str | None = None,
    ) -> list[SubstitutionLog]:
        raise NotImplementedError

    @abstractmethod
    def save(self, log: SubstitutionLog) -> SubstitutionLog:
        raise NotImplementedError

    @abstractmethod
    def get_busy_teacher_ids(self, date: str, period: int) -> set[str]:
        raise NotImplementedError

    @abstractmethod
    def get_intervention_counts(self) -> dict[str, int]:
        raise NotImplementedError

    @abstractmethod
    def get_last_used_at(self, teacher_ids: list[str], period: int) -> dict[str, datetime]:
        raise NotImplementedError
