from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class SlotStatus(str, Enum):
    FREE = "FREE"
    TEACHING = "TEACHING"
    ABSENCE = "ABSENCE"


@dataclass(frozen=True)
class TimeSlot:
    date: str      # Formato ISO: "YYYY-MM-DD" (ej. "2026-09-21")
    day_index: int # 0: Lunes, ..., 4: Viernes
    period: int    # 0 a 5

    @property
    def label(self) -> str:
        days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        return f"{days[self.day_index]} ({self.date}) - P{self.period}"


@dataclass
class Teacher:
    id: str  # Almacena el GUID
    name: str
    department: str = "General"


@dataclass
class TeacherSchedule:
    teacher_id: str
    # Mapeo de (date, period) -> SlotStatus
    slots: dict[tuple[str, int], SlotStatus] = field(default_factory=dict)

    def is_available(self, slot: TimeSlot) -> bool:
        return self.slots.get((slot.date, slot.period), SlotStatus.FREE) == SlotStatus.FREE


@dataclass
class GuardAssignment:
    slot: TimeSlot
    assigned_teachers: list[str]
    required_count: int = 2

    @property
    def deficit(self) -> int:
        return max(0, self.required_count - len(self.assigned_teachers))


@dataclass
class AssignmentReport:
    assignments: list[GuardAssignment]
    guard_counts_by_teacher: dict[str, int]
    deficit_incidents: list[str]
    solver_status: str
    is_optimal: bool

    @property
    def total_deficits(self) -> int:
        return sum(a.deficit for a in self.assignments)

    @property
    def max_difference_in_load(self) -> int:
        if not self.guard_counts_by_teacher:
            return 0
        counts = list(self.guard_counts_by_teacher.values())
        return max(counts) - min(counts)