import pytest

from src.domain.email_settings import (
    DEFAULT_BODY_TEMPLATE,
    DEFAULT_SUBJECT_TEMPLATE,
    EmailConfiguration,
    EmailTemplate,
    SmtpSettings,
)
from src.infrastructure.email.configuration_provider import (
    env_email_configuration,
    resolve_email_configuration,
)

SMTP_ENV = {
    "SMTP_HOST": "smtp.env.es",
    "SMTP_PORT": "2525",
    "SMTP_USER": "env@centro.es",
    "SMTP_PASS": "env-clave",
    "SENDER_EMAIL": "env@centro.es",
}


class FakeRepository:
    def __init__(self, config=None):
        self.config = config

    def get(self):
        return self.config

    def save(self, config):
        self.config = config


def _stored():
    return EmailConfiguration(
        smtp=SmtpSettings(
            host="smtp.db.es",
            port=465,
            user="db@centro.es",
            password="db-clave",
            sender_email="db@centro.es",
        ),
        template=EmailTemplate("Asunto BD", "Cuerpo BD {teacher_name}"),
    )


def test_stored_configuration_wins_over_environment(monkeypatch):
    for key, value in SMTP_ENV.items():
        monkeypatch.setenv(key, value)

    config = resolve_email_configuration(FakeRepository(_stored()))

    assert config.smtp.host == "smtp.db.es"
    assert config.template.subject == "Asunto BD"


def test_falls_back_to_environment_when_nothing_is_stored(monkeypatch):
    for key, value in SMTP_ENV.items():
        monkeypatch.setenv(key, value)

    config = resolve_email_configuration(FakeRepository(None))

    assert config.smtp.host == "smtp.env.es"
    assert config.smtp.port == 2525
    assert config.smtp.password == "env-clave"
    assert config.template.subject == DEFAULT_SUBJECT_TEMPLATE
    assert config.template.body == DEFAULT_BODY_TEMPLATE


def test_missing_environment_names_every_missing_variable(monkeypatch):
    for key in SMTP_ENV:
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(RuntimeError, match="SMTP_HOST") as error:
        env_email_configuration()

    assert "SENDER_EMAIL" in str(error.value)
