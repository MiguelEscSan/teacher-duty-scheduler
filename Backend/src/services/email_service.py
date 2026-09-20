import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

logger = logging.getLogger("EmailService")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "guardias@centroeducativo.es")


def send_urgent_substitution_email(
    to_email: str,
    teacher_name: str,
    group_name: str,
    period: int,
    date_str: str,
    absent_teacher_name: str,
):
    """Envío en background de notificación formal de sustitución corta."""
    subject = f"URGENTE: Asignación de sustitución corta - {date_str} P{period}"
    body = (
        f"Estimado/a {teacher_name},\n\n"
        f"Aviso de guardia urgente: Debes cubrir al grupo [{group_name}] en el periodo [P{period}] "
        f"el día [{date_str}] por ausencia de [{absent_teacher_name}].\n\n"
        f"Por favor, acude al aula con puntualidad.\n"
        f"Equipo Directivo / Jefatura de Estudios."
    )

    if not SMTP_USER or not SMTP_PASS:
        logger.warning(
            f"[MOCK EMAIL] Para: {to_email} | Asunto: {subject} | Mensaje: {body.replace(chr(10), ' ')}"
        )
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        logger.info(f"Correo de sustitución enviado a {to_email}")
    except Exception as exc:
        logger.error(f"Fallo al enviar correo a {to_email}: {exc}")