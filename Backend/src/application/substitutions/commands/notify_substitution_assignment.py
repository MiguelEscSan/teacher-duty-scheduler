from dataclasses import dataclass

from src.application.common.mediator import Command, RequestHandler
from src.domain.email import EmailMessage, EmailRecipient
from src.domain.ports.email_sender import EmailSender
from src.domain.repositories.student_group_repository import StudentGroupRepository
from src.domain.repositories.teacher_repository import TeacherRepository


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
    def __init__(
        self,
        teacher_repository: TeacherRepository,
        student_group_repository: StudentGroupRepository,
        email_sender: EmailSender,
    ):
        self.teacher_repository = teacher_repository
        self.student_group_repository = student_group_repository
        self.email_sender = email_sender

    def handle(self, cmd: NotifySubstitutionAssignmentCommand) -> bool:
        substitute = self.teacher_repository.get_by_id(cmd.substitute_teacher_id)
        absent = self.teacher_repository.get_by_id(cmd.absent_teacher_id)
        if not substitute or not absent:
            raise ValueError("Docentes no encontrados.")
        group = (
            self.student_group_repository.get_by_id(cmd.group_id)
            if cmd.group_id else None
        )
        group_name = group.name if group else "Sin grupo asignado"
        email = EmailMessage(
            to=EmailRecipient(str(substitute.email)),
            subject=f"URGENTE: Asignación de guardia - {cmd.date} P{cmd.period}",
            body=(
                f"Estimado/a {substitute.name},\n\n"
                f"Debes cubrir al grupo [{group_name}] en el periodo [P{cmd.period}] "
                f"el día [{cmd.date}] por ausencia de [{absent.name}].\n\n"
                "Por favor, acude al aula con puntualidad."
            ),
        )
        return self.email_sender.send(email)
