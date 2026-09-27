# src/infrastructure/email/smtp_email_sender.py
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from src.domain.email import EmailMessage
from src.domain.ports.email_sender import EmailSender

logger = logging.getLogger("SMTPEmailSender")
load_dotenv()


class SMTPEmailSender(EmailSender):
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        self.smtp_pass = smtp_pass.replace(" ", "") if smtp_pass else None
        self.sender_email = os.getenv("SENDER_EMAIL")

        missing = [
            name
            for name, value in {
                "SMTP_HOST": self.smtp_host,
                "SMTP_USER": self.smtp_user,
                "SMTP_PASS": self.smtp_pass,
                "SENDER_EMAIL": self.sender_email,
            }.items()
            if not value
        ]
        if missing:
            raise RuntimeError(
                "Faltan variables de entorno SMTP requeridas: " + ", ".join(missing)
            )

        try:
            self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        except ValueError as exc:
            raise RuntimeError("SMTP_PORT debe ser un número entero.") from exc

    def send(self, message: EmailMessage) -> bool:
        try:
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = message.to.email
            msg["Subject"] = message.subject
            msg.attach(MIMEText(message.body, "plain", "utf-8"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            logger.info(f"Correo enviado exitosamente a {message.to.email}")
            return True
        except Exception as exc:
            logger.exception(f"Fallo al enviar correo a {message.to.email}: {exc}")
            return False