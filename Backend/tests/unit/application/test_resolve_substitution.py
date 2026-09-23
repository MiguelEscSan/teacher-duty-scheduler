import pytest

from src.api.schemas import ResolutionAction
from src.application.substitutions.commands.resolve_substitution import (
    ResolveSubstitutionCommand,
    ResolveSubstitutionHandler,
)
from src.domain.absence import Absence
from src.domain.exceptions.absence_already_resolved_exception import AbsenceAlreadyResolvedException
from src.domain.student_group import StudentGroup
from src.domain.teacher import Teacher


def make_handler(fakes, teachers, fixed=None, short=None, groups=None):
    fakes["teachers"].items = teachers
    fakes["schedules"].fixed = fixed or {}
    fakes["schedules"].short = short or {}
    fakes["groups"].items = groups or []
    return ResolveSubstitutionHandler(
        fakes["teachers"], fakes["absences"], fakes["schedules"],
        fakes["substitutions"], fakes["groups"],
    )


@pytest.mark.unit
@pytest.mark.parametrize("action", [ResolutionAction.EXCURSION, ResolutionAction.MERGE_GROUPS])
def test_resolve_non_covering_actions_without_substitute(fakes, action):
    teachers = [Teacher.create("Ana Díaz", teacher_id="absent")]
    groups = [
        StudentGroup.create("1A", 10, group_id="group-1"),
        StudentGroup.create("1B", 12, group_id="group-2"),
    ]
    handler = make_handler(fakes, teachers, groups=groups)

    result = handler.handle(ResolveSubstitutionCommand(
        "2026-09-21", 1, "absent", action, "group-1", "group-2"
    ))

    assert result.resolved is True
    assert result.substitute_id is None
    assert result.action_applied == action.value
    assert fakes["absences"].get_by_slot("absent", "2026-09-21", 1).resolved is True


@pytest.mark.unit
def test_auto_assign_keeps_a_teacher_in_staff_room(fakes):
    teachers = [
        Teacher.create("Absent", teacher_id="absent"),
        Teacher.create("First", teacher_id="first"),
        Teacher.create("Second", teacher_id="second"),
    ]
    handler = make_handler(fakes, teachers, fixed={(0, 1): ["first", "second"]})

    result = handler.handle(ResolveSubstitutionCommand(
        "2026-09-21", 1, "absent", ResolutionAction.AUTO_ASSIGN
    ))

    assert result.resolved is True
    assert result.is_fixed_duty_substitute is True
    assert result.staff_room_keeper_name in {"First", "Second"}
    assert result.substitute_id in {"first", "second"}
    assert result.substitute_id != "absent"


@pytest.mark.unit
def test_auto_assign_falls_back_to_short_term_when_ordinary_has_one_candidate(fakes):
    teachers = [
        Teacher.create("Absent", teacher_id="absent"),
        Teacher.create("Short", teacher_id="short"),
    ]
    handler = make_handler(
        fakes, teachers, fixed={(0, 1): ["short"]}, short={(0, 1): ["short"]}
    )

    result = handler.handle(ResolveSubstitutionCommand(
        "2026-09-21", 1, "absent", ResolutionAction.AUTO_ASSIGN
    ))

    assert result.resolved is True
    assert result.is_short_term_substitute is True
    assert result.substitute_id == "short"


@pytest.mark.unit
def test_force_short_term_ignores_ordinary_list(fakes):
    teachers = [
        Teacher.create("Absent", teacher_id="absent"),
        Teacher.create("Short", teacher_id="short"),
    ]
    handler = make_handler(fakes, teachers, fixed={(0, 1): ["short"]}, short={(0, 1): ["short"]})

    result = handler.handle(ResolveSubstitutionCommand(
        "2026-09-21", 1, "absent", ResolutionAction.FORCE_SHORT_TERM
    ))

    assert result.resolved is True
    assert result.source_type == "SHORT_TERM_SUBSTITUTION"


@pytest.mark.unit
def test_resolve_reports_alert_when_both_lists_are_exhausted(fakes):
    handler = make_handler(
        fakes, [Teacher.create("Absent", teacher_id="absent")]
    )

    result = handler.handle(ResolveSubstitutionCommand(
        "2026-09-21", 1, "absent", ResolutionAction.AUTO_ASSIGN
    ))

    assert result.resolved is False
    assert "Sin profesores disponibles" in result.details


@pytest.mark.unit
def test_resolve_rejects_an_absence_that_was_already_resolved(fakes):
    teachers = [Teacher.create("Absent", teacher_id="absent")]
    fakes["absences"].items = [Absence.create("absent", "2026-09-21", 1)]
    fakes["absences"].items[0].mark_as_do_not_cover()
    handler = make_handler(fakes, teachers)

    with pytest.raises(AbsenceAlreadyResolvedException):
        handler.handle(ResolveSubstitutionCommand(
            "2026-09-21", 1, "absent", ResolutionAction.EXCURSION
        ))


@pytest.mark.unit
def test_resolve_rejects_unknown_absent_teacher(fakes):
    handler = make_handler(fakes, [])

    with pytest.raises(ValueError, match="no encontrado"):
        handler.handle(ResolveSubstitutionCommand(
            "2026-09-21", 1, "missing", ResolutionAction.AUTO_ASSIGN
        ))


@pytest.mark.unit
def test_resolve_does_not_reuse_busy_or_absent_candidates(fakes):
    teachers = [
        Teacher.create("Absent", teacher_id="absent"),
        Teacher.create("Other absent", teacher_id="other-absent"),
        Teacher.create("Busy", teacher_id="busy"),
        Teacher.create("Available", teacher_id="available"),
    ]
    fakes["absences"].items = [Absence.create("other-absent", "2026-09-21", 1)]
    old_log = fakes["substitutions"]
    old_log.logs = []
    from src.domain.substitution import SubstitutionLog, SubstitutionSourceType
    old_log.save(SubstitutionLog.create(
        "2026-09-21", 1, "x", "busy", SubstitutionSourceType.MANUAL
    ))
    handler = make_handler(
        fakes, teachers, fixed={(0, 1): ["other-absent", "busy", "available", "absent"]}
    )

    result = handler.handle(ResolveSubstitutionCommand(
        "2026-09-21", 1, "absent", ResolutionAction.AUTO_ASSIGN
    ))

    assert result.resolved is False
    assert "Sin profesores disponibles" in result.details
