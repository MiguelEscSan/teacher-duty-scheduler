import pytest

from src.domain.email_settings import (
    DEFAULT_BODY_TEMPLATE,
    DEFAULT_SUBJECT_TEMPLATE,
    EmailTemplate,
    SmtpSettings,
)

VALUES = {
    "teacher_name": "Eva López",
    "absent_teacher_name": "Juan Pérez",
    "group_name": "1º ESO A",
    "period": 2,
    "date": "2026-09-21",
}


def test_default_template_renders_the_original_assignment_text():
    template = EmailTemplate(DEFAULT_SUBJECT_TEMPLATE, DEFAULT_BODY_TEMPLATE)

    subject, body = template.render(VALUES)

    assert subject == "URGENTE: Asignación de guardia - 2026-09-21 P2"
    assert body.startswith("Estimado/a Eva López,")
    assert "[1º ESO A]" in body
    assert "[P2]" in body
    assert "[Juan Pérez]" in body


def test_template_rejects_unknown_placeholder():
    with pytest.raises(ValueError, match="unknown_field"):
        EmailTemplate("Hola {unknown_field}", "Cuerpo {teacher_name}")


def test_template_rejects_empty_subject_or_body():
    with pytest.raises(ValueError):
        EmailTemplate("   ", "Cuerpo")
    with pytest.raises(ValueError):
        EmailTemplate("Asunto", "")


def test_template_rejects_malformed_braces():
    with pytest.raises(ValueError):
        EmailTemplate("Hola {teacher_name", "Cuerpo")


def test_smtp_settings_require_host_user_and_sender():
    with pytest.raises(ValueError):
        SmtpSettings(host="", port=587, user="a@b.es", password="x", sender_email="a@b.es")


@pytest.mark.parametrize("port", [0, 65536, -1])
def test_smtp_settings_reject_out_of_range_port(port):
    with pytest.raises(ValueError):
        SmtpSettings(host="smtp.x.es", port=port, user="a@b.es", password="x", sender_email="a@b.es")


def test_smtp_settings_accept_valid_values():
    settings = SmtpSettings(
        host="smtp.x.es", port=587, user="a@b.es", password="x", sender_email="a@b.es"
    )
    assert settings.port == 587
