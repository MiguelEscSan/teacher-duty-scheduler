# src/application/substitutions/commands/notify_substitution_assignment.py
from dataclasses import dataclass
from sqlmodel import Session
from src.application.common.mediator import Command, RequestHandler
from src.domain.email import EmailMessage, EmailRecipient
from src.domain.ports.email_sender import EmailSender
from src.infrastructure.db.models import TeacherDB, StudentGroupDB


@dataclass(frozen=True)
class NotifySubstitutionAssignmentCommand(Command[bool]):
    date: str
    period: int
    absent_teacher_id: str
    substitute_teacher_id: str
    group_id: str | None = None


class NotifySubstitutionAssignmentHandler(
    RequestHandler[NotifySubstitutionAssignmentCommand, bool]
):
    def __init__(self, session: Session, email_sender: EmailSender):
        self.session = session
        self.email_sender = email_sender

    def handle(self, cmd: NotifySubstitutionAssignmentCommand) -> bool:
        substitute = self.session.get(TeacherDB, cmd.substitute_teacher_id)
        absent = self.session.get(TeacherDB, cmd.absent_teacher_id)

        if not substitute or not absent:
            raise ValueError("Docentes no encontrados.")

        group_name = "Sin grupo asignado"
        if cmd.group_id:
            group = self.session.get(StudentGroupDB, cmd.group_id)
            if group:
                group_name = group.name

        # La plantilla de negocio se ensambla aquí, pero el mensaje final es un EmailMessage puro
        subject = f"URGENTE: Asignación de guardia - {cmd.date} P{cmd.period}"
        body = (
            f"Estimado/a {substitute.name},\n\n"
            f"Debes cubrir al grupo [{group_name}] en el periodo [P{cmd.period}] "
            f"el día [{cmd.date}] por ausencia de [{absent.name}].\n\n"
            f"Por favor, acude al aula con puntualidad."
        )

        email = EmailMessage(
            to=EmailRecipient(substitute.email),
            subject=subject,
            body=body,
        )
        return self.email_sender.send(email)