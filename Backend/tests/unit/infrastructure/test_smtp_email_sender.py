import smtplib

from src.domain.email import EmailMessage, EmailRecipient
from src.domain.email_settings import EmailConfiguration, EmailTemplate, SmtpSettings
from src.infrastructure.email.smtp_email_sender import SMTPEmailSender

SENDER_MODULE = "src.infrastructure.email.smtp_email_sender"


def _config(port=587):
    return EmailConfiguration(
        smtp=SmtpSettings(
            host="smtp.gmail.com",
            port=port,
            user="avisos@centro.es",
            password="clave",
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
        self.started_tls = False
        self.logged_in = None
        self.sent = None
        type(self).instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def starttls(self):
        self.started_tls = True

    def close(self):
        pass

    def login(self, user, password):
        self.logged_in = (user, password)

    def send_message(self, msg):
        self.sent = msg


class RecordingSMTPSSL(RecordingSMTP):
    pass


def test_port_587_uses_starttls_and_sends_from_the_user(monkeypatch):
    RecordingSMTP.instances = []
    monkeypatch.setattr(f"{SENDER_MODULE}.smtplib.SMTP", RecordingSMTP)

    assert SMTPEmailSender(lambda: _config(587)).send(_message()) is True

    server = RecordingSMTP.instances[0]
    assert (server.host, server.port) == ("smtp.gmail.com", 587)
    assert server.started_tls is True
    assert server.logged_in == ("avisos@centro.es", "clave")
    assert server.sent["From"] == "avisos@centro.es"


def test_port_465_uses_implicit_tls(monkeypatch):
    RecordingSMTPSSL.instances = []
    monkeypatch.setattr(f"{SENDER_MODULE}.smtplib.SMTP_SSL", RecordingSMTPSSL)

    assert SMTPEmailSender(lambda: _config(465)).send(_message()) is True

    server = RecordingSMTPSSL.instances[0]
    assert server.port == 465
    assert server.started_tls is False
    assert server.logged_in == ("avisos@centro.es", "clave")


def test_returns_false_when_smtp_fails(monkeypatch):
    class FailingSMTP(RecordingSMTP):
        def login(self, user, password):
            raise smtplib.SMTPAuthenticationError(535, b"bad credentials")

    monkeypatch.setattr(f"{SENDER_MODULE}.smtplib.SMTP", FailingSMTP)

    assert SMTPEmailSender(lambda: _config()).send(_message()) is False


def test_returns_false_when_configuration_cannot_be_loaded():
    def broken():
        raise RuntimeError("Faltan variables de entorno SMTP requeridas: SMTP_USER")

    assert SMTPEmailSender(broken).send(_message()) is False
