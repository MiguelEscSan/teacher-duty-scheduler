from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.domain.exceptions.absence_already_resolved_exception import AbsenceAlreadyResolvedException
from src.domain.exceptions.invalid_operation_exception import InvalidOperationException
from src.domain.substitution import SubstitutionSourceType, SubstitutionLog
from src.domain.teacher import generate_id

if TYPE_CHECKING:
    pass


@dataclass
class Absence:
    id: str
    teacher_id: str
    date: str
    period: int
    reason: str
    resolved: bool = False

    @classmethod
    def create(cls, teacher_id: str, date: str, period: int, reason: str = "Permiso / Asunto propio") -> Absence:
        if not 0 <= period <= 5:
            raise InvalidOperationException(f"El periodo {period} está fuera del rango válido (0 a 5).")
        return cls(generate_id(), teacher_id, date, period, reason)

    def _ensure_not_resolved(self) -> None:
        if self.resolved:
            raise AbsenceAlreadyResolvedException(self.id)

    def mark_as_do_not_cover(self) -> None:
        self._ensure_not_resolved()
        self.resolved = True

    def resolve_by_excursion(self) -> None:
        self._ensure_not_resolved()
        self.resolved = True

    def resolve_by_group_merge(self) -> None:
        self._ensure_not_resolved()
        self.resolved = True

    def resolve_by_merge(self) -> None:
        self.resolve_by_group_merge()

    def resolve_with_substitute(
        self, substitute_teacher_id: str, source_type: SubstitutionSourceType,
        group_id: str | None = None,
    ) -> SubstitutionLog:
        self._ensure_not_resolved()
        log = SubstitutionLog.create(
            self.date, self.period, self.teacher_id, substitute_teacher_id, source_type, group_id
        )
        self.resolved = True
        return log
