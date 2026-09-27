from dataclasses import dataclass


@dataclass(frozen=True)
class AbsenceResponseDto:
    id: str
    teacher_id: str
    teacher_name: str
    date: str
    period: int
    resolved: bool
    group_id: str | None = None
    group_name: str = ""
    student_count: int | None = None
    reason: str = ""
