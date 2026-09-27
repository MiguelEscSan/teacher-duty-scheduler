from dataclasses import dataclass

from src.application.teachers.dtos.teacher_response import TeacherResponseDto


@dataclass(frozen=True)
class DutySlotDto:
    day_of_week: int
    day_name: str
    period: int
    teachers: list[TeacherResponseDto]
