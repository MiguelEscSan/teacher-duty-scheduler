# src/infrastructure/repositories/email_settings_repository.py
from sqlmodel import Session

from src.domain.email_settings import EmailConfiguration, EmailTemplate, SmtpSettings
from src.domain.ports.email_settings_repository import EmailSettingsRepository
from src.infrastructure.db.models import EmailSettingsDB
from src.infrastructure.security.secret_box import SecretBox

SETTINGS_ROW_ID = "default"


class SQLEmailSettingsRepository(EmailSettingsRepository):
    """Guarda correo, contraseña cifrada y plantilla. Host y puerto los fija el servidor."""

    def __init__(self, session: Session, secret_box: SecretBox, host: str, port: int):
        self.session = session
        self.secret_box = secret_box
        self.host = host
        self.port = port

    def get(self) -> EmailConfiguration | None:
        record = self.session.get(EmailSettingsDB, SETTINGS_ROW_ID)
        if record is None:
            return None
        return EmailConfiguration(
            smtp=SmtpSettings(
                host=self.host,
                port=self.port,
                user=record.smtp_user,
                password=self.secret_box.decrypt(record.smtp_password_encrypted),
            ),
            template=EmailTemplate(record.subject_template, record.body_template),
        )

    def save(self, config: EmailConfiguration) -> None:
        record = self.session.get(EmailSettingsDB, SETTINGS_ROW_ID)
        if record is None:
            record = EmailSettingsDB(
                id=SETTINGS_ROW_ID,
                smtp_user="",
                smtp_password_encrypted="",
                subject_template="",
                body_template="",
            )
            self.session.add(record)
        record.smtp_user = config.smtp.user
        record.smtp_password_encrypted = self.secret_box.encrypt(config.smtp.password)
        record.subject_template = config.template.subject
        record.body_template = config.template.body
        self.session.flush()
