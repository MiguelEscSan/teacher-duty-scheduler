from dataclasses import dataclass


@dataclass(frozen=True)
class AvailableTeacherDto:
    id: str
    name: str
    department: str
    duty_type: str
    interventions_count: int
