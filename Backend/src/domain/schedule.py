from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import TYPE_CHECKING

from src.domain.exceptions.invalid_operation_exception import InvalidOperationException

if TYPE_CHECKING:
    from src.domain.student_group import StudentGroup


class SlotStatus(str, Enum):
    FREE = "FREE"
    TEACHING = "TEACHING"
    ABSENCE = "ABSENCE"
    DUTY = "DUTY"


@dataclass(frozen=True)
class TimeSlot:
    date: str
    day_index: int
    period: int
    week: int = 0

    def __post_init__(self) -> None:
        if not 0 <= self.day_index <= 4:
            raise InvalidOperationException("El día debe estar entre 0 y 4.")
        if not 0 <= self.period <= 5:
            raise InvalidOperationException("El periodo debe estar entre 0 y 5.")
        try:
            date.fromisoformat(self.date)
        except (TypeError, ValueError) as exc:
            raise InvalidOperationException("La fecha debe tener formato ISO (YYYY-MM-DD).") from exc

    @property
    def day(self) -> int:
        return self.day_index

    @property
    def label(self) -> str:
        days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        return f"{days[self.day_index]} ({self.date}) - P{self.period}"


@dataclass
class ScheduleSlot:
    slot: TimeSlot
    status: SlotStatus = SlotStatus.FREE
    assigned_group: StudentGroup | None = None

    @property
    def time_slot(self) -> TimeSlot:
        return self.slot

    def assign_group(self, group: StudentGroup) -> None:
        if self.status not in (SlotStatus.FREE, SlotStatus.TEACHING):
            raise InvalidOperationException("La franja no está disponible para asignar un grupo.")
        self.assigned_group = group
        self.status = SlotStatus.TEACHING

    def release_to_free(self) -> None:
        self.assigned_group = None
        self.status = SlotStatus.FREE


@dataclass
class TeacherSchedule:
    teacher_id: str
    slots: dict[tuple[str, int], SlotStatus] = field(default_factory=dict)

    def is_available(self, slot: TimeSlot) -> bool:
        return self.slots.get((slot.date, slot.period), SlotStatus.FREE) == SlotStatus.FREE
