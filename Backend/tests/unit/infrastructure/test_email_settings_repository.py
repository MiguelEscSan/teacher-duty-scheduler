from sqlmodel import select

from src.domain.email_settings import EmailConfiguration, EmailTemplate, SmtpSettings
from src.infrastructure.db.models import EmailSettingsDB
from src.infrastructure.repositories.email_settings_repository import (
    SQLEmailSettingsRepository,
)
from src.infrastructure.security.secret_box import SecretBox


def _config(password="clave-secreta"):
    return EmailConfiguration(
        smtp=SmtpSettings(
            host="smtp.centro.es",
            port=587,
            user="avisos@centro.es",
            password=password,
            sender_email="avisos@centro.es",
        ),
        template=EmailTemplate("Asunto {date}", "Cuerpo {teacher_name}"),
    )


def test_get_returns_none_when_nothing_is_saved(db_session, tmp_path):
    repository = SQLEmailSettingsRepository(db_session, SecretBox(tmp_path / "secret.key"))

    assert repository.get() is None


def test_save_then_get_round_trips_settings(db_session, tmp_path):
    repository = SQLEmailSettingsRepository(db_session, SecretBox(tmp_path / "secret.key"))

    repository.save(_config())
    loaded = repository.get()

    assert loaded.smtp.host == "smtp.centro.es"
    assert loaded.smtp.port == 587
    assert loaded.smtp.password == "clave-secreta"
    assert loaded.template.subject == "Asunto {date}"


def test_save_overwrites_the_single_row(db_session, tmp_path):
    repository = SQLEmailSettingsRepository(db_session, SecretBox(tmp_path / "secret.key"))

    repository.save(_config(password="primera"))
    repository.save(_config(password="segunda"))

    rows = db_session.exec(select(EmailSettingsDB)).all()
    assert len(rows) == 1
    assert repository.get().smtp.password == "segunda"


def test_password_is_stored_encrypted(db_session, tmp_path):
    repository = SQLEmailSettingsRepository(db_session, SecretBox(tmp_path / "secret.key"))

    repository.save(_config(password="clave-secreta"))

    row = db_session.exec(select(EmailSettingsDB)).one()
    assert "clave-secreta" not in row.smtp_password_encrypted
