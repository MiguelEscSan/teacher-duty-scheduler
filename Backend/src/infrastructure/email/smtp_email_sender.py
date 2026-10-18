# src/infrastructure/email/smtp_email_sender.py
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Callable

from src.domain.email import EmailMessage
from src.domain.email_settings import EmailConfiguration, SmtpSettings
from src.domain.ports.email_sender import EmailSender

logger = logging.getLogger("SMTPEmailSender")


class SMTPEmailSender(EmailSender):
    """Envía correos con la configuración SMTP vigente en cada envío."""

    def __init__(self, load_configuration: Callable[[], EmailConfiguration]):
        self.load_configuration = load_configuration

    def send(self, message: EmailMessage) -> bool:
        try:
            smtp = self.load_configuration().smtp

            msg = MIMEMultipart()
            msg["From"] = smtp.sender_email
            msg["To"] = message.to.email
            msg["Subject"] = message.subject
            msg.attach(MIMEText(message.body, "plain", "utf-8"))

            with self._connect(smtp) as server:
                server.login(smtp.user, smtp.password)
                server.send_message(msg)

            logger.info(f"Correo enviado exitosamente a {message.to.email}")
            return True
        except Exception as exc:
            logger.exception(f"Fallo al enviar correo a {message.to.email}: {exc}")
            return False

    @staticmethod
    def _connect(smtp: SmtpSettings):
        # Puerto 465: TLS desde el inicio. Otros puertos (587): STARTTLS.
        if smtp.uses_implicit_tls:
            return smtplib.SMTP_SSL(smtp.host, smtp.port)
        server = smtplib.SMTP(smtp.host, smtp.port)
        try:
            server.starttls()
        except Exception:
            server.close()
            raise
        return server
