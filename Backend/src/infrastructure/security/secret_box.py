# src/infrastructure/security/secret_box.py
from pathlib import Path

from cryptography.fernet import Fernet


class SecretBox:
    """Cifrado simétrico (Fernet) para secretos guardados en BBDD.

    La clave se genera la primera vez y se guarda en `key_path`. Protege el
    secreto si solo se copia el fichero de BBDD; no protege frente a quien
    tenga acceso a la carpeta completa de datos.
    """

    def __init__(self, key_path: Path):
        self.key_path = Path(key_path)
        self._fernet_instance: Fernet | None = None

    def encrypt(self, plain_text: str) -> str:
        return self._fernet().encrypt(plain_text.encode("utf-8")).decode("ascii")

    def decrypt(self, token: str) -> str:
        return self._fernet().decrypt(token.encode("ascii")).decode("utf-8")

    def _fernet(self) -> Fernet:
        # Perezoso: la clave solo se crea cuando hace falta cifrar o descifrar.
        if self._fernet_instance is None:
            if not self.key_path.is_file():
                self.key_path.parent.mkdir(parents=True, exist_ok=True)
                self.key_path.write_bytes(Fernet.generate_key())
            self._fernet_instance = Fernet(self.key_path.read_bytes())
        return self._fernet_instance
