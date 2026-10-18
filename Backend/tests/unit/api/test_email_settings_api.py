import pytest

from src.infrastructure.security.secret_box import SecretBox

PAYLOAD = {
    "smtp_user": "avisos@centro.es",
    "smtp_password": "clave-secreta",
    "subject_template": "Guardia {date} P{period}",
    "body_template": "Hola {teacher_name}, cubres a {absent_teacher_name}.",
}


@pytest.fixture(autouse=True)
def isolated_settings(monkeypatch, tmp_path):
    for name in ("SMTP_HOST", "SMTP_USER", "SMTP_PASS", "SENDER_EMAIL", "SMTP_PORT"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(
        "src.api.dependencies.get_secret_box",
        lambda: SecretBox(tmp_path / "secret.key"),
    )


class RecordingSMTP:
    sent = []

    def __init__(self, host, port):
        self.host, self.port = host, port

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def starttls(self):
        pass

    def login(self, user, password):
        pass

    def send_message(self, msg):
        RecordingSMTP.sent.append(msg)


def test_get_reports_no_configuration_when_nothing_is_saved(client):
    response = client.get("/api/v1/email/settings")

    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "none"
    assert body["has_password"] is False


def test_put_saves_settings_and_never_returns_the_password(client):
    response = client.put("/api/v1/email/settings", json=PAYLOAD)

    assert response.status_code == 200
    assert "clave-secreta" not in response.text
    body = client.get("/api/v1/email/settings").json()
    assert body["source"] == "database"
    assert body["smtp_user"] == "avisos@centro.es"
    assert body["has_password"] is True
    assert body["subject_template"] == "Guardia {date} P{period}"


def test_put_without_password_keeps_the_stored_one(client):
    client.put("/api/v1/email/settings", json=PAYLOAD)

    response = client.put(
        "/api/v1/email/settings", json={**PAYLOAD, "smtp_password": ""}
    )

    assert response.status_code == 200
    assert client.get("/api/v1/email/settings").json()["has_password"] is True


def test_put_without_any_password_is_rejected(client):
    response = client.put(
        "/api/v1/email/settings", json={**PAYLOAD, "smtp_password": None}
    )

    assert response.status_code == 400
    assert "contraseña" in response.json()["detail"].lower()


def test_put_rejects_unknown_placeholder(client):
    response = client.put(
        "/api/v1/email/settings",
        json={**PAYLOAD, "body_template": "Hola {nombre_inventado}"},
    )

    assert response.status_code == 400
    assert "nombre_inventado" in response.json()["detail"]


def test_test_endpoint_sends_a_message_with_saved_settings(client, monkeypatch):
    RecordingSMTP.sent = []
    monkeypatch.setattr("src.infrastructure.email.smtp_email_sender.smtplib.SMTP", RecordingSMTP)
    client.put("/api/v1/email/settings", json=PAYLOAD)

    response = client.post("/api/v1/email/settings/test", json={"to": "docente@centro.es"})

    assert response.status_code == 200
    assert response.json() == {"sent": True}
    assert RecordingSMTP.sent[0]["To"] == "docente@centro.es"


def test_test_endpoint_rejects_invalid_recipient(client):
    response = client.post("/api/v1/email/settings/test", json={"to": "no-es-correo"})

    assert response.status_code == 400
