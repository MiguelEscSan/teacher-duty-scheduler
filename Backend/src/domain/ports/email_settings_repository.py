# src/domain/ports/email_settings_repository.py
from abc import ABC, abstractmethod

from src.domain.email_settings import EmailConfiguration


class EmailSettingsRepository(ABC):
    """Puerto de salida para persistir la configuración de correo (fila única)."""

    @abstractmethod
    def get(self) -> EmailConfiguration | None:
        """Devuelve la configuración guardada o None si nunca se ha configurado."""

    @abstractmethod
    def save(self, config: EmailConfiguration) -> None:
        """Crea o sustituye la configuración guardada."""
