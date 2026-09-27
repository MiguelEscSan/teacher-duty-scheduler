from dataclasses import dataclass


@dataclass(frozen=True)
class StudentGroupResponseDto:
    id: str
    name: str
    student_count: int | None = None
