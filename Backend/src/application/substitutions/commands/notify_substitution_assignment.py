from dataclasses import dataclass
from typing import Callable

from src.application.common.mediator import Command, RequestHandler
from src.domain.email import EmailMessage, EmailRecipient
from src.domain.email_settings import (
    DEFAULT_BODY_TEMPLATE,
    DEFAULT_SUBJECT_TEMPLATE,
    EmailTemplate,
)
from src.domain.ports.email_sender import EmailSender
from src.domain.ports.student_group_repository import StudentGroupRepository
from src.domain.ports.teacher_repository import TeacherRepository


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
        template_provider: Callable[[], EmailTemplate] | None = None,
    ):
        self.teacher_repository = teacher_repository
        self.student_group_repository = student_group_repository
        self.email_sender = email_sender
        self.template_provider = template_provider or (
            lambda: EmailTemplate(DEFAULT_SUBJECT_TEMPLATE, DEFAULT_BODY_TEMPLATE)
        )

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
        subject, body = self.template_provider().render({
            "teacher_name": substitute.name,
            "absent_teacher_name": absent.name,
            "group_name": group_name,
            "period": cmd.period,
            "date": cmd.date,
        })
        email = EmailMessage(
            to=EmailRecipient(str(substitute.email)),
            subject=subject,
            body=body,
        )
        return self.email_sender.send(email)
