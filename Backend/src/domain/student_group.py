from __future__ import annotations

import uuid
from dataclasses import dataclass

from src.domain.exceptions.domain_exception import CapacityExceededException
from src.domain.exceptions.invalid_operation_exception import InvalidOperationException


@dataclass
class StudentGroup:
    id: str
    name: str
    student_count: int = 0
    max_capacity: int = 30

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.name.strip():
            raise InvalidOperationException("El grupo debe tener identificador y nombre.")
        if self.student_count < 0:
            raise InvalidOperationException("El número de alumnos no puede ser negativo.")
        if self.max_capacity <= 0:
            raise InvalidOperationException("El aforo debe ser mayor que cero.")
        if self.student_count > self.max_capacity:
            raise CapacityExceededException(
                f"El grupo '{self.name}' supera su aforo de {self.max_capacity} alumnos."
            )

    @classmethod
    def create(
        cls,
        name: str,
        student_count: int = 0,
        max_capacity: int = 30,
        group_id: str | None = None,
    ) -> StudentGroup:
        return cls(
            id=group_id.strip() if group_id else str(uuid.uuid4()),
            name=name,
            student_count=student_count,
            max_capacity=max_capacity,
        )

    @property
    def capacity(self) -> int:
        return self.max_capacity

    def merge_with(self, other: StudentGroup) -> StudentGroup:
        total = self.student_count + other.student_count
        if total > self.max_capacity:
            raise CapacityExceededException(
                f"La fusión de '{self.name}' y '{other.name}' supera el aforo de "
                f"{self.max_capacity} alumnos."
            )
        self.student_count = total
        return self
