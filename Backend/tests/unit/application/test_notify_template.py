from src.application.substitutions.commands.notify_substitution_assignment import (
    NotifySubstitutionAssignmentCommand,
    NotifySubstitutionAssignmentHandler,
)
from src.domain.email_settings import EmailTemplate


class RecordingEmailSender:
    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(message)
        return True


def test_notification_uses_the_configured_template(fakes, teacher_factory):
    substitute = teacher_factory("Eva López", teacher_id="sub")
    absent = teacher_factory("Juan Pérez", teacher_id="abs")
    fakes["teachers"].save(substitute)
    fakes["teachers"].save(absent)
    sender = RecordingEmailSender()
    template = EmailTemplate("Guardia {date} hora {period}", "Hola {teacher_name}, cubres a {absent_teacher_name}.")

    NotifySubstitutionAssignmentHandler(
        fakes["teachers"], fakes["groups"], sender, lambda: template
    ).handle(NotifySubstitutionAssignmentCommand(
        date="2026-09-21",
        period=2,
        absent_teacher_id="abs",
        substitute_teacher_id="sub",
    ))

    message = sender.messages[0]
    assert message.subject == "Guardia 2026-09-21 hora 2"
    assert message.body == "Hola Eva López, cubres a Juan Pérez."
