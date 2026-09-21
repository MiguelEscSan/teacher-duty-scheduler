# src/domain/ports/email_sender.py
from abc import ABC, abstractmethod
from src.domain.email import EmailMessage


class EmailSender(ABC):
    """Puerto de salida (Driven Port) para el envío de correos electrónicos."""

    @abstractmethod
    def send(self, message: EmailMessage) -> bool:
        """Envía el correo electrónico de forma sincrónica o programada."""
        pass