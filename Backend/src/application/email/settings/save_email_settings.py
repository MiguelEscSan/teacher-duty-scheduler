# src/application/email/settings/save_email_settings.py
from dataclasses import dataclass

from src.application.common.mediator import Command, RequestHandler
from src.application.email.settings.dtos import EmailSettingsView, view_from
from src.domain.email_settings import EmailConfiguration, EmailTemplate, SmtpSettings
from src.domain.ports.email_settings_repository import EmailSettingsRepository


@dataclass(frozen=True)
class SaveEmailSettingsCommand(Command[EmailSettingsView]):
    smtp_user: str
    subject_template: str
    body_template: str
    # Vacía o None: se conserva la contraseña ya guardada.
    smtp_password: str | None = None


class SaveEmailSettingsHandler(RequestHandler[SaveEmailSettingsCommand, EmailSettingsView]):
    def __init__(self, repository: EmailSettingsRepository, host: str, port: int):
        self.repository = repository
        self.host = host
        self.port = port

    def handle(self, cmd: SaveEmailSettingsCommand) -> EmailSettingsView:
        stored = self.repository.get()
        password = cmd.smtp_password or (stored.smtp.password if stored else "")
        config = EmailConfiguration(
            smtp=SmtpSettings(
                host=self.host,
                port=self.port,
                user=cmd.smtp_user,
                password=password,
            ),
            template=EmailTemplate(cmd.subject_template, cmd.body_template),
        )
        self.repository.save(config)
        return view_from(config, "database")
