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


IMPLICIT_TLS_PORT = 465  # SMTPS: TLS desde el inicio de la conexión
STARTTLS_PORT = 587  # Conexión plana que se eleva a TLS con STARTTLS


@dataclass(frozen=True)
class SmtpSettings:
    """Transporte SMTP. El remitente es siempre la cuenta que se autentica."""

    host: str
    port: int
    user: str
    password: str

    def __post_init__(self):
        if not self.host.strip():
            raise ValueError("El servidor SMTP es obligatorio.")
        # Google muestra las contraseñas de aplicación con espacios; no forman parte del secreto.
        object.__setattr__(self, "password", self.password.replace(" ", ""))
        if not self.password:
            raise ValueError("La contraseña SMTP es obligatoria.")
        if not 1 <= self.port <= 65535:
            raise ValueError("El puerto SMTP debe estar entre 1 y 65535.")
        EmailRecipient(self.user)

    @property
    def sender_email(self) -> str:
        return self.user

    @property
    def uses_implicit_tls(self) -> bool:
        return self.port == IMPLICIT_TLS_PORT


@dataclass(frozen=True)
class EmailConfiguration:
    """Configuración completa de correo: transporte SMTP y plantilla del mensaje."""

    smtp: SmtpSettings
    template: EmailTemplate
