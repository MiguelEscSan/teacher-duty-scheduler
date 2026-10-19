# src/infrastructure/email/configuration_provider.py
import os

from src.domain.email_settings import (
    DEFAULT_BODY_TEMPLATE,
    DEFAULT_SUBJECT_TEMPLATE,
    STARTTLS_PORT,
    EmailConfiguration,
    EmailTemplate,
    SmtpSettings,
)
from src.domain.ports.email_settings_repository import EmailSettingsRepository

DEFAULT_SMTP_HOST = "smtp.gmail.com"


def smtp_server_from_env() -> tuple[str, int]:
    """Servidor SMTP del sistema. Lo fijamos nosotros; las variables solo sobrescriben (Docker)."""
    host = os.getenv("SMTP_HOST") or DEFAULT_SMTP_HOST
    try:
        port = int(os.getenv("SMTP_PORT") or STARTTLS_PORT)
    except ValueError as exc:
        raise RuntimeError("SMTP_PORT debe ser un número entero.") from exc
    return host, port


def env_email_configuration() -> EmailConfiguration:
    """Configuración heredada de las variables de entorno (Docker, desarrollo)."""
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    missing = [name for name, value in (("SMTP_USER", user), ("SMTP_PASS", password)) if not value]
    if missing:
        raise RuntimeError(
            "Faltan variables de entorno SMTP requeridas: " + ", ".join(missing)
        )
    host, port = smtp_server_from_env()
    return EmailConfiguration(
        smtp=SmtpSettings(
            host=host,
            port=port,
            user=user,
            password=password,
        ),
        template=EmailTemplate(DEFAULT_SUBJECT_TEMPLATE, DEFAULT_BODY_TEMPLATE),
    )


def resolve_email_configuration(repository: EmailSettingsRepository) -> EmailConfiguration:
    """La configuración guardada en BBDD tiene prioridad; si no existe, se usa el entorno."""
    return repository.get() or env_email_configuration()
