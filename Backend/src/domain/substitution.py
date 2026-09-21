from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.domain.exceptions.invalid_operation_exception import InvalidOperationException
from src.domain.teacher import generate_id


class SubstitutionSourceType(str, Enum):
    ORDINARY_GUARD = "ORDINARY_GUARD"
    SHORT_TERM_SUBSTITUTION = "SHORT_TERM_SUBSTITUTION"
    MANUAL = "MANUAL"


@dataclass
class SubstitutionLog:
    id: str
    date: str
    period: int
    absent_teacher_id: str
    substitute_teacher_id: str
    source_type: SubstitutionSourceType
    group_id: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls, date: str, period: int, absent_teacher_id: str,
        substitute_teacher_id: str, source_type: SubstitutionSourceType,
        group_id: str | None = None,
    ) -> SubstitutionLog:
        if absent_teacher_id == substitute_teacher_id:
            raise InvalidOperationException("Un docente no puede sustituirse a sí mismo.")
        return cls(generate_id(), date, period, absent_teacher_id, substitute_teacher_id, source_type, group_id)
