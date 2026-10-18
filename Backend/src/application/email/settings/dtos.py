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
    smtp_host: str
    smtp_port: int
    smtp_user: str
    sender_email: str
    has_password: bool
    subject_template: str
    body_template: str


def view_from(config: EmailConfiguration, source: str) -> EmailSettingsView:
    return EmailSettingsView(
        source=source,
        smtp_host=config.smtp.host,
        smtp_port=config.smtp.port,
        smtp_user=config.smtp.user,
        sender_email=config.smtp.sender_email,
        has_password=bool(config.smtp.password),
        subject_template=config.template.subject,
        body_template=config.template.body,
    )


def empty_view() -> EmailSettingsView:
    return EmailSettingsView(
        source="none",
        smtp_host="",
        smtp_port=587,
        smtp_user="",
        sender_email="",
        has_password=False,
        subject_template=DEFAULT_SUBJECT_TEMPLATE,
        body_template=DEFAULT_BODY_TEMPLATE,
    )
