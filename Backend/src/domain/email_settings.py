# src/domain/email_settings.py
from dataclasses import dataclass
from string import Formatter

from src.domain.email import EmailRecipient

PLACEHOLDERS = frozenset(
    {"teacher_name", "absent_teacher_name", "group_name", "period", "date"}
)

DEFAULT_SUBJECT_TEMPLATE = "URGENTE: Asignación de guardia - {date} P{period}"
DEFAULT_BODY_TEMPLATE = (
    "Estimado/a {teacher_name},\n\n"
    "Debes cubrir al grupo [{group_name}] en el periodo [P{period}] "
    "el día [{date}] por ausencia de [{absent_teacher_name}].\n\n"
    "Por favor, acude al aula con puntualidad."
)


@dataclass(frozen=True)
class EmailTemplate:
    """Asunto y cuerpo con placeholders validados contra PLACEHOLDERS."""

    subject: str
    body: str

    def __post_init__(self):
        if not self.subject.strip():
            raise ValueError("El asunto de la plantilla no puede estar vacío.")
        if not self.body.strip():
            raise ValueError("El cuerpo de la plantilla no puede estar vacío.")
        for text in (self.subject, self.body):
            _check_placeholders(text)

    def render(self, values: dict) -> tuple[str, str]:
        return self.subject.format_map(values), self.body.format_map(values)


def _check_placeholders(text: str) -> None:
    # Formatter.parse lanza ValueError si las llaves están mal cerradas.
    for _, field_name, _, _ in Formatter().parse(text):
        if field_name is not None and field_name not in PLACEHOLDERS:
            raise ValueError(f"Placeholder desconocido: {{{field_name}}}")


@dataclass(frozen=True)
class SmtpSettings:
    """Configuración de salida SMTP. Value Object validado al construirse."""

    host: str
    port: int
    user: str
    password: str
    sender_email: str

    def __post_init__(self):
        if not self.host.strip():
            raise ValueError("El servidor SMTP es obligatorio.")
        if not self.password:
            raise ValueError("La contraseña SMTP es obligatoria.")
        if not 1 <= self.port <= 65535:
            raise ValueError("El puerto SMTP debe estar entre 1 y 65535.")
        EmailRecipient(self.user)
        EmailRecipient(self.sender_email)


@dataclass(frozen=True)
class EmailConfiguration:
    """Configuración completa de correo: transporte SMTP y plantilla del mensaje."""

    smtp: SmtpSettings
    template: EmailTemplate
