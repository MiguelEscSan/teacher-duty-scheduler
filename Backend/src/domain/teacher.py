from __future__ import annotations

import re
import unicodedata
import uuid
from dataclasses import dataclass

from src.domain.exceptions.invalid_operation_exception import InvalidOperationException


def generate_id() -> str:
    return str(uuid.uuid4())


@dataclass(frozen=True)
class CorporateEmail:
    """Value object for normalized corporate teacher addresses."""

    value: str
    domain: str = "centro.edu"

    def __post_init__(self) -> None:
        value = self.value.strip().lower()
        if not re.fullmatch(r"[a-z0-9]+(?:[._-][a-z0-9]+)*@[a-z0-9.-]+", value):
            raise ValueError(f"Dirección de correo corporativo inválida: '{self.value}'")
        object.__setattr__(self, "value", value)

    @classmethod
    def from_teacher_name(cls, name: str, domain: str = "centro.edu") -> CorporateEmail:
        normalized = unicodedata.normalize("NFKD", name)
        ascii_name = "".join(char for char in normalized if not unicodedata.combining(char))
        parts = re.findall(r"[a-z0-9]+", ascii_name.lower())
        if not parts:
            raise ValueError("El nombre del docente no permite generar un correo.")
        return cls(f"{'.'.join(parts)}@{domain.strip().lower()}", domain.strip().lower())

    @property
    def email(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.value


@dataclass
class Teacher:
    id: str
    name: str
    department: str = "General"
    email: CorporateEmail | None = None

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise InvalidOperationException("El identificador del docente no puede estar vacío.")
        if not self.name or not self.name.strip():
            raise InvalidOperationException("El nombre del docente no puede estar vacío.")
        self.id = self.id.strip()
        self.name = self.name.strip()
        self.department = self.department.strip() or "General"
        if self.email is not None and not isinstance(self.email, CorporateEmail):
            self.email = CorporateEmail(str(self.email))

    @classmethod
    def create(
        cls,
        name: str,
        department: str = "General",
        email: CorporateEmail | str | None = None,
        teacher_id: str | None = None,
    ) -> Teacher:
        if teacher_id is not None and not teacher_id.strip():
            raise InvalidOperationException("El identificador del docente no puede estar vacío.")
        corporate_email = (
            CorporateEmail.from_teacher_name(name) if email is None
            else email if isinstance(email, CorporateEmail)
            else CorporateEmail(email)
        )
        return cls(
            id=teacher_id.strip() if teacher_id else generate_id(),
            name=name,
            department=department,
            email=corporate_email,
        )
