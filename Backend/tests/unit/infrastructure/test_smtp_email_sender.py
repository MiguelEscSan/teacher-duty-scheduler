import smtplib

from src.domain.email import EmailMessage, EmailRecipient
from src.domain.email_settings import EmailConfiguration, EmailTemplate, SmtpSettings
from src.infrastructure.email.smtp_email_sender import SMTPEmailSender


def _config():
    return EmailConfiguration(
        smtp=SmtpSettings(
            host="smtp.centro.es",
            port=587,
            user="avisos@centro.es",
            password="clave",
            sender_email="notificaciones@centro.es",
        ),
        template=EmailTemplate("Asunto", "Cuerpo"),
    )


def _message():
    return EmailMessage(
        to=EmailRecipient("docente@centro.es"), subject="Asunto", body="Cuerpo"
    )


class RecordingSMTP:
    instances = []

    def __init__(self, host, port):
        self.host, self.port = host, port
        self.logged_in = None
        self.sent = None
        RecordingSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def starttls(self):
        pass

    def login(self, user, password):
        self.logged_in = (user, password)

    def send_message(self, msg):
        self.sent = msg


def test_sends_with_stored_settings(monkeypatch):
    RecordingSMTP.instances = []
    monkeypatch.setattr("src.infrastructure.email.smtp_email_sender.smtplib.SMTP", RecordingSMTP)

    sender = SMTPEmailSender(lambda: _config())

    assert sender.send(_message()) is True
    server = RecordingSMTP.instances[0]
    assert (server.host, server.port) == ("smtp.centro.es", 587)
    assert server.logged_in == ("avisos@centro.es", "clave")
    assert server.sent["From"] == "notificaciones@centro.es"


def test_returns_false_when_smtp_fails(monkeypatch):
    class FailingSMTP(RecordingSMTP):
        def login(self, user, password):
            raise smtplib.SMTPAuthenticationError(535, b"bad credentials")

    monkeypatch.setattr("src.infrastructure.email.smtp_email_sender.smtplib.SMTP", FailingSMTP)

    assert SMTPEmailSender(lambda: _config()).send(_message()) is False


def test_returns_false_when_configuration_cannot_be_loaded():
    def broken():
        raise RuntimeError("Faltan variables de entorno SMTP requeridas: SMTP_HOST")

    assert SMTPEmailSender(broken).send(_message()) is False
