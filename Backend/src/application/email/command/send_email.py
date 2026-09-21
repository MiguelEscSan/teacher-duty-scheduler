# src/application/email/commands/send_email.py
from dataclasses import dataclass
from src.application.common.mediator import Command, RequestHandler
from src.domain.email import EmailMessage, EmailRecipient
from src.domain.ports.email_sender import EmailSender


@dataclass(frozen=True)
class SendEmailCommand(Command[bool]):
    to: str
    subject: str
    body: str


class SendEmailHandler(RequestHandler[SendEmailCommand, bool]):
    def __init__(self, email_sender: EmailSender):
        self.email_sender = email_sender

    def handle(self, cmd: SendEmailCommand) -> bool:
        # Construcción y validación mediante la entidad y Value Objects de dominio
        recipient = EmailRecipient(cmd.to)
        message = EmailMessage(
            to=recipient,
            subject=cmd.subject,
            body=cmd.body,
        )
        return self.email_sender.send(message)