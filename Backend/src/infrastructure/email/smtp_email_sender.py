# src/infrastructure/email/smtp_email_sender.py
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.domain.email import EmailMessage
from src.domain.ports.email_sender import EmailSender

logger = logging.getLogger("SMTPEmailSender")


class SMTPEmailSender(EmailSender):
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_pass = os.getenv("SMTP_PASS", "")
        self.sender_email = os.getenv("SENDER_EMAIL", "notificaciones@centroeducativo.es")

    def send(self, message: EmailMessage) -> bool:
        if not self.smtp_user or not self.smtp_pass:
            logger.warning(
                f"[MOCK EMAIL] To: {message.to.email} | Subject: {message.subject} | "
                f"Body: {message.body.replace(chr(10), ' ')}"
            )
            return True

        try:
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = message.to.email
            msg["Subject"] = message.subject
            msg.attach(MIMEText(message.body, "plain"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            logger.info(f"Correo enviado exitosamente a {message.to.email}")
            return True
        except Exception as exc:
            logger.error(f"Fallo al enviar correo a {message.to.email}: {exc}")
            return False