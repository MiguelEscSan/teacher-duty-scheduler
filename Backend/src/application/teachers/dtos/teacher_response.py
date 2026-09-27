from dataclasses import dataclass


@dataclass(frozen=True)
class TeacherResponseDto:
    id: str
    name: str
    department: str
    email: str | None = None
