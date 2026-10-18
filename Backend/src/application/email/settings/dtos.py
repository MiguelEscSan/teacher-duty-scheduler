# src/application/email/settings/dtos.py
from dataclasses import dataclass

from src.domain.email_settings import (
    DEFAULT_BODY_TEMPLATE,
    DEFAULT_SUBJECT_TEMPLATE,
    EmailConfiguration,
)


@dataclass(frozen=True)
class EmailSettingsView:
    """Vista de la configuración de correo. Nunca incluye la contraseña."""

    source: str  # "database", "environment" o "none"
    smtp_user: str  # Correo que se usa para autenticarse y como remitente
    has_password: bool
    subject_template: str
    body_template: str


def view_from(config: EmailConfiguration, source: str) -> EmailSettingsView:
    return EmailSettingsView(
        source=source,
        smtp_user=config.smtp.user,
        has_password=bool(config.smtp.password),
        subject_template=config.template.subject,
        body_template=config.template.body,
    )


def empty_view() -> EmailSettingsView:
    return EmailSettingsView(
        source="none",
        smtp_user="",
        has_password=False,
        subject_template=DEFAULT_SUBJECT_TEMPLATE,
        body_template=DEFAULT_BODY_TEMPLATE,
    )
