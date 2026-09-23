from datetime import datetime

import pytest

from src.application.substitutions.queries.get_available_candidates import (
    GetAvailableCandidatesHandler,
    GetAvailableCandidatesQuery,
)
from src.application.substitutions.queries.get_substitution_history import (
    GetSubstitutionHistoryHandler,
    GetSubstitutionHistoryQuery,
)
from src.domain.absence import Absence
from src.domain.schedule import ScheduleEntry
from src.domain.student_group import StudentGroup
from src.domain.substitution import SubstitutionLog, SubstitutionSourceType
from src.domain.teacher import Teacher


@pytest.mark.unit
def test_available_candidates_excludes_absent_busy_and_teaching_teachers(fakes):
    teachers = [
        Teacher.create("Fixed", teacher_id="fixed"),
        Teacher.create("Short", teacher_id="short"),
        Teacher.create("Free", teacher_id="free"),
        Teacher.create("Absent", teacher_id="absent"),
        Teacher.create("Busy", teacher_id="busy"),
        Teacher.create("Teaching", teacher_id="teaching"),
    ]
    fakes["teachers"].items = teachers
    fakes["absences"].items = [Absence.create("absent", "2026-09-21", 1)]
    fakes["schedules"].fixed = {(0, 1): ["fixed"]}
    fakes["schedules"].short = {(0, 1): ["short"]}
    fakes["schedules"].entries = [ScheduleEntry("teaching", 0, 1, is_teaching=True)]
    fakes["substitutions"].save(SubstitutionLog.create(
        "2026-09-21", 1, "other", "busy", SubstitutionSourceType.MANUAL
    ))

    result = GetAvailableCandidatesHandler(
        fakes["teachers"], fakes["absences"], fakes["schedules"], fakes["substitutions"]
    ).handle(GetAvailableCandidatesQuery("2026-09-21", 1))

    assert [item.id for item in result] == ["fixed", "short", "free"]
    assert result[0].duty_type == "FIXED_DUTY"
    assert result[1].duty_type == "SHORT_TERM"


@pytest.mark.unit
def test_available_candidates_returns_empty_on_weekend(fakes):
    result = GetAvailableCandidatesHandler(
        fakes["teachers"], fakes["absences"], fakes["schedules"], fakes["substitutions"]
    ).handle(GetAvailableCandidatesQuery("2026-09-20", 1))

    assert result == []


@pytest.mark.unit
def test_available_candidates_sort_by_duty_then_interventions_then_name(fakes):
    first = Teacher.create("Zoe", teacher_id="first")
    second = Teacher.create("Ana", teacher_id="second")
    fakes["teachers"].items = [first, second]
    fakes["schedules"].fixed = {(0, 1): ["first", "second"]}
    for _ in range(2):
        fakes["substitutions"].save(SubstitutionLog.create(
            "2026-09-20", 1, "x", "first", SubstitutionSourceType.MANUAL
        ))

    result = GetAvailableCandidatesHandler(
        fakes["teachers"], fakes["absences"], fakes["schedules"], fakes["substitutions"]
    ).handle(GetAvailableCandidatesQuery("2026-09-21", 1))

    assert [item.id for item in result] == ["second", "first"]
    assert result[1].interventions_count == 2


@pytest.mark.unit
def test_history_enriches_teacher_and_group_names(fakes):
    absent = Teacher.create("Ana Díaz", teacher_id="absent")
    substitute = Teacher.create("Eva López", teacher_id="substitute")
    fakes["teachers"].items = [absent, substitute]
    fakes["groups"].items = [StudentGroup.create("1A", group_id="group-1")]
    log = SubstitutionLog.create(
        "2026-09-21", 1, "absent", "substitute",
        SubstitutionSourceType.ORDINARY_GUARD, "group-1"
    )
    fakes["substitutions"].logs = [log]

    result = GetSubstitutionHistoryHandler(
        fakes["substitutions"], fakes["teachers"], fakes["groups"]
    ).handle(GetSubstitutionHistoryQuery("2026-09-21", "substitute", "absent"))

    assert len(result) == 1
    assert result[0].substitute_teacher_name == "Eva López"
    assert result[0].absent_teacher_name == "Ana Díaz"
    assert result[0].group_name == "1A"
    assert result[0].source_type == "ORDINARY_GUARD"


@pytest.mark.unit
def test_history_uses_fallbacks_for_missing_referenced_entities(fakes):
    log = SubstitutionLog.create(
        "2026-09-21", 1, "absent", "substitute", SubstitutionSourceType.MANUAL
    )
    fakes["substitutions"].logs = [log]

    result = GetSubstitutionHistoryHandler(
        fakes["substitutions"], fakes["teachers"], fakes["groups"]
    ).handle(GetSubstitutionHistoryQuery())

    assert result[0].substitute_teacher_name == "Profesor no encontrado"
    assert result[0].absent_teacher_name == "Profesor no encontrado"
    assert result[0].group_name is None
