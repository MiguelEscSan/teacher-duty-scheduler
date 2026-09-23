from datetime import datetime

import pytest

from src.api.schemas import ResolutionAction
from src.application.substitutions.commands.assign_manual_substitution import (
    AssignManualSubstitutionCommand,
    AssignManualSubstitutionHandler,
)
from src.application.substitutions.commands.mark_absence_do_not_cover import (
    MarkAbsenceDoNotCoverCommand,
    MarkAbsenceDoNotCoverHandler,
)
from src.application.substitutions.commands.notify_substitution_assignment import (
    NotifySubstitutionAssignmentCommand,
    NotifySubstitutionAssignmentHandler,
)
from src.domain.absence import Absence
from src.domain.exceptions.invalid_operation_exception import InvalidOperationException
from src.domain.student_group import StudentGroup
from src.domain.substitution import SubstitutionLog, SubstitutionSourceType
from src.domain.teacher import Teacher


class RecordingEmailSender:
    def __init__(self, result=True):
        self.result = result
        self.messages = []

    def send(self, message):
        self.messages.append(message)
        return self.result


@pytest.mark.unit
def test_manual_assignment_creates_absence_log_and_resolves_absence(fakes):
    absence_repo = fakes["absences"]
    substitution_repo = fakes["substitutions"]
    handler = AssignManualSubstitutionHandler(absence_repo, substitution_repo)

    result = handler.handle(AssignManualSubstitutionCommand(
        "2026-09-21", 1, "absent", "substitute", "group-1"
    ))

    assert result["message"] == "Sustitución manual asignada correctamente"
    assert absence_repo.get_by_slot("absent", "2026-09-21", 1).resolved is True
    assert substitution_repo.logs[0].source_type is SubstitutionSourceType.MANUAL
    assert substitution_repo.logs[0].group_id == "group-1"


@pytest.mark.unit
def test_manual_assignment_updates_existing_history_for_absent_teacher(fakes):
    absence_repo = fakes["absences"]
    substitution_repo = fakes["substitutions"]
    absence_repo.save(Absence.create("absent", "2026-09-21", 1))
    existing = SubstitutionLog.create(
        "2026-09-21", 1, "absent", "old-substitute", SubstitutionSourceType.MANUAL
    )
    substitution_repo.save(existing)

    result = AssignManualSubstitutionHandler(
        absence_repo, substitution_repo
    ).handle(AssignManualSubstitutionCommand(
        "2026-09-21", 1, "absent", "new-substitute"
    ))

    assert result["message"] == "Sustitución manual asignada correctamente"
    assert substitution_repo.logs[0].substitute_teacher_id == "new-substitute"


@pytest.mark.unit
def test_manual_assignment_does_not_overwrite_history_from_another_period(fakes):
    substitution_repo = fakes["substitutions"]
    previous = SubstitutionLog.create(
        "2026-09-21", 0, "absent", "old-substitute", SubstitutionSourceType.MANUAL
    )
    substitution_repo.save(previous)

    AssignManualSubstitutionHandler(
        fakes["absences"], substitution_repo
    ).handle(AssignManualSubstitutionCommand(
        "2026-09-21", 1, "absent", "new-substitute"
    ))

    assert len(substitution_repo.logs) == 2
    assert substitution_repo.logs[0].substitute_teacher_id == "old-substitute"
    assert substitution_repo.logs[1].substitute_teacher_id == "new-substitute"


@pytest.mark.unit
def test_manual_assignment_rejects_self_substitution(fakes):
    with pytest.raises(InvalidOperationException, match="sustituirse a sí mismo"):
        AssignManualSubstitutionHandler(
            fakes["absences"], fakes["substitutions"]
        ).handle(AssignManualSubstitutionCommand(
            "2026-09-21", 1, "same", "same"
        ))


@pytest.mark.unit
def test_do_not_cover_rejects_unknown_absence(fakes):
    with pytest.raises(ValueError, match="Ausencia no encontrada"):
        MarkAbsenceDoNotCoverHandler(fakes["absences"]).handle(
            MarkAbsenceDoNotCoverCommand("2026-09-21", 1, "missing")
        )


@pytest.mark.unit
def test_do_not_cover_marks_existing_absence_resolved(fakes, absence_factory):
    absence = absence_factory(period=1)
    fakes["absences"].save(absence)

    result = MarkAbsenceDoNotCoverHandler(fakes["absences"]).handle(
        MarkAbsenceDoNotCoverCommand(absence.date, absence.period, absence.teacher_id)
    )

    assert result == {"message": "Ausencia marcada como no cubrir.", "resolved": True}


@pytest.mark.unit
def test_notify_sends_message_with_group_and_all_assignment_details(fakes):
    substitute = Teacher.create("Eva López", teacher_id="substitute")
    absent = Teacher.create("Ana Díaz", teacher_id="absent")
    fakes["teachers"].items = [substitute, absent]
    fakes["groups"].items = [StudentGroup.create("1A", group_id="group-1")]
    sender = RecordingEmailSender()

    result = NotifySubstitutionAssignmentHandler(
        fakes["teachers"], fakes["groups"], sender
    ).handle(NotifySubstitutionAssignmentCommand(
        "2026-09-21", 2, "absent", "substitute", "group-1"
    ))

    assert result is True
    assert sender.messages[0].to.email == "eva@centroeducativo.es"
    assert sender.messages[0].subject == "URGENTE: Asignación de guardia - 2026-09-21 P2"
    assert "1A" in sender.messages[0].body
    assert "Ana Díaz" in sender.messages[0].body


@pytest.mark.unit
@pytest.mark.parametrize("missing_id", ["absent", "substitute"])
def test_notify_rejects_missing_teacher(fakes, missing_id):
    substitute = Teacher.create("Eva López", teacher_id="substitute")
    absent = Teacher.create("Ana Díaz", teacher_id="absent")
    fakes["teachers"].items = [substitute, absent]
    fakes["teachers"].items = [item for item in fakes["teachers"].items if item.id != missing_id]

    with pytest.raises(ValueError, match="Docentes no encontrados"):
        NotifySubstitutionAssignmentHandler(
            fakes["teachers"], fakes["groups"], RecordingEmailSender()
        ).handle(NotifySubstitutionAssignmentCommand(
            "2026-09-21", 2, "absent", "substitute"
        ))


@pytest.mark.unit
def test_notify_uses_fallback_group_name_and_propagates_sender_result(fakes):
    substitute = Teacher.create("Eva López", teacher_id="substitute")
    absent = Teacher.create("Ana Díaz", teacher_id="absent")
    fakes["teachers"].items = [substitute, absent]
    sender = RecordingEmailSender(result=False)

    result = NotifySubstitutionAssignmentHandler(
        fakes["teachers"], fakes["groups"], sender
    ).handle(NotifySubstitutionAssignmentCommand(
        "2026-09-21", 2, "absent", "substitute"
    ))

    assert result is False
    assert "Sin grupo asignado" in sender.messages[0].body
