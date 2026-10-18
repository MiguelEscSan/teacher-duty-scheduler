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
    "SMTP_USER": "env@centro.es",
    "SMTP_PASS": "env-clave",
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
            host="smtp.gmail.com",
            port=587,
            user="db@centro.es",
            password="db-clave",
        ),
        template=EmailTemplate("Asunto BD", "Cuerpo BD {teacher_name}"),
    )


@pytest.fixture
def clean_env(monkeypatch):
    for name in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "SENDER_EMAIL"):
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def test_stored_configuration_wins_over_environment(clean_env):
    for key, value in SMTP_ENV.items():
        clean_env.setenv(key, value)

    config = resolve_email_configuration(FakeRepository(_stored()))

    assert config.smtp.user == "db@centro.es"
    assert config.template.subject == "Asunto BD"


def test_falls_back_to_environment_with_default_server(clean_env):
    for key, value in SMTP_ENV.items():
        clean_env.setenv(key, value)

    config = resolve_email_configuration(FakeRepository(None))

    assert config.smtp.host == "smtp.gmail.com"
    assert config.smtp.port == 587
    assert config.smtp.user == "env@centro.es"
    assert config.smtp.sender_email == "env@centro.es"
    assert config.template.subject == DEFAULT_SUBJECT_TEMPLATE
    assert config.template.body == DEFAULT_BODY_TEMPLATE


def test_environment_can_override_the_server(clean_env):
    for key, value in SMTP_ENV.items():
        clean_env.setenv(key, value)
    clean_env.setenv("SMTP_HOST", "smtp.otro.es")
    clean_env.setenv("SMTP_PORT", "465")

    config = env_email_configuration()

    assert (config.smtp.host, config.smtp.port) == ("smtp.otro.es", 465)


def test_missing_environment_names_every_missing_variable(clean_env):
    with pytest.raises(RuntimeError, match="SMTP_USER") as error:
        env_email_configuration()

    assert "SMTP_PASS" in str(error.value)
