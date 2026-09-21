# src/domain/email.py
from dataclasses import dataclass
import re

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


@dataclass(frozen=True)
class EmailRecipient:
    """Value Object para asegurar la validez del correo electrónico."""
    value: str

    def __post_init__(self):
        if not self.value or not EMAIL_REGEX.match(self.value.strip()):
            raise ValueError(f"Dirección de correo electrónico inválida: '{self.value}'")

    @property
    def email(self) -> str:
        return self.value.strip().lower()


@dataclass(frozen=True)
class EmailMessage:
    """Entidad pura de dominio que representa un mensaje de correo electrónico."""
    to: EmailRecipient
    subject: str
    body: str

    def __post_init__(self):
        if not self.subject.strip():
            raise ValueError("El asunto del correo no puede estar vacío.")
        if not self.body.strip():
            raise ValueError("El cuerpo del correo no puede estar vacío.")