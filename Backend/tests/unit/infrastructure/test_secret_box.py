from src.infrastructure.security.secret_box import SecretBox


def test_encrypt_then_decrypt_returns_original_text(tmp_path):
    box = SecretBox(tmp_path / "secret.key")

    token = box.encrypt("contraseña")

    assert token != "contraseña"
    assert box.decrypt(token) == "contraseña"


def test_key_file_is_created_once_and_reused(tmp_path):
    key_path = tmp_path / "secret.key"
    token = SecretBox(key_path).encrypt("valor")

    assert key_path.is_file()
    assert SecretBox(key_path).decrypt(token) == "valor"
