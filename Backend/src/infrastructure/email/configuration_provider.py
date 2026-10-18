# src/infrastructure/email/configuration_provider.py
import os

from src.domain.email_settings import (
    DEFAULT_BODY_TEMPLATE,
    DEFAULT_SUBJECT_TEMPLATE,
    EmailConfiguration,
    EmailTemplate,
    SmtpSettings,
)
from src.domain.ports.email_settings_repository import EmailSettingsRepository

REQUIRED_ENV_VARS = ("SMTP_HOST", "SMTP_USER", "SMTP_PASS", "SENDER_EMAIL")


def env_email_configuration() -> EmailConfiguration:
    """Configuración heredada de las variables de entorno (Docker, desarrollo)."""
    values = {name: os.getenv(name) for name in REQUIRED_ENV_VARS}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError(
            "Faltan variables de entorno SMTP requeridas: " + ", ".join(missing)
        )
    try:
        port = int(os.getenv("SMTP_PORT", "587"))
    except ValueError as exc:
        raise RuntimeError("SMTP_PORT debe ser un número entero.") from exc

    return EmailConfiguration(
        smtp=SmtpSettings(
            host=values["SMTP_HOST"],
            port=port,
            user=values["SMTP_USER"],
            password=values["SMTP_PASS"].replace(" ", ""),
            sender_email=values["SENDER_EMAIL"],
        ),
        template=EmailTemplate(DEFAULT_SUBJECT_TEMPLATE, DEFAULT_BODY_TEMPLATE),
    )


def resolve_email_configuration(repository: EmailSettingsRepository) -> EmailConfiguration:
    """La configuración guardada en BBDD tiene prioridad; si no existe, se usa el entorno."""
    return repository.get() or env_email_configuration()
