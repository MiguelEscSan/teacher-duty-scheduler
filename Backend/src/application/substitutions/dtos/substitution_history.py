from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SubstitutionHistoryDto:
    id: str
    date: str
    period: int
    substitute_teacher_id: str
    substitute_teacher_name: str
    absent_teacher_id: str
    absent_teacher_name: str
    group_id: str | None
    group_name: str | None
    source_type: str
    created_at: datetime
