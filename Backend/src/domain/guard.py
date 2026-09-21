from __future__ import annotations

from dataclasses import dataclass

from src.domain.schedule import TimeSlot


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
        return sum(assignment.deficit for assignment in self.assignments)

    @property
    def max_difference_in_load(self) -> int:
        if not self.guard_counts_by_teacher:
            return 0
        counts = list(self.guard_counts_by_teacher.values())
        return max(counts) - min(counts)
