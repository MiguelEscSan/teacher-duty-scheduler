from datetime import datetime, timedelta

import pytest

from src.domain.absence import Absence
from src.application.substitutions.services.auto_cover_teacher_duties import (
    AutoCoverTeacherDutiesService,
)
from src.domain.substitution import SubstitutionLog, SubstitutionSourceType
from src.domain.teacher import Teacher


def make_matcher(fakes, teachers, fixed=None, short=None):
    fakes["teachers"].items = teachers
    fakes["schedules"].fixed = fixed or {}
    fakes["schedules"].short = short or {}
    return AutoCoverTeacherDutiesService(
        fakes["teachers"],
        fakes["absences"],
        fakes["schedules"],
        fakes["substitutions"],
    )


@pytest.mark.unit
def test_matcher_keeps_one_ordinary_teacher_in_the_staff_room(fakes):
    teachers = [
        Teacher.create("First", teacher_id="first"),
        Teacher.create("Second", teacher_id="second"),
    ]
    matcher = make_matcher(fakes, teachers, fixed={(0, 1): ["first", "second"]})

    result = matcher.select_candidate("2026-09-21", 0, 1)

    assert result.source_type is SubstitutionSourceType.ORDINARY_GUARD
    assert {result.substitute.id, result.staff_room_keeper.id} == {"first", "second"}
    assert result.substitute.id != result.staff_room_keeper.id


@pytest.mark.unit
def test_matcher_filters_absent_and_busy_teachers_before_applying_rotation(fakes):
    teachers = [
        Teacher.create("Absent", teacher_id="absent"),
        Teacher.create("Busy", teacher_id="busy"),
        Teacher.create("Available", teacher_id="available"),
        Teacher.create("Keeper", teacher_id="keeper"),
    ]
    fakes["absences"].items = [Absence.create("absent", "2026-09-21", 1)]
    fakes["substitutions"].save(
        SubstitutionLog.create(
            "2026-09-21", 1, "other", "busy", SubstitutionSourceType.MANUAL
        )
    )
    matcher = make_matcher(
        fakes,
        teachers,
        fixed={(0, 1): ["absent", "busy", "available", "keeper"]},
    )

    result = matcher.select_candidate("2026-09-21", 0, 1)

    assert result.substitute.id == "available"
    assert result.staff_room_keeper.id == "keeper"


@pytest.mark.unit
def test_matcher_rotates_to_the_least_recently_used_teacher(fakes):
    teachers = [
        Teacher.create("First", teacher_id="first"),
        Teacher.create("Second", teacher_id="second"),
    ]
    older = SubstitutionLog.create(
        "2026-09-20", 1, "other", "first", SubstitutionSourceType.MANUAL
    )
    older.created_at = datetime.utcnow() - timedelta(days=2)
    newer = SubstitutionLog.create(
        "2026-09-20", 1, "other", "second", SubstitutionSourceType.MANUAL
    )
    newer.created_at = datetime.utcnow() - timedelta(days=1)
    fakes["substitutions"].logs = [older, newer]
    matcher = make_matcher(
        fakes,
        teachers,
        fixed={(0, 1): ["first", "second"]},
    )

    result = matcher.select_candidate("2026-09-21", 0, 1)

    assert result.substitute.id == "first"


@pytest.mark.unit
def test_matcher_escalates_to_short_term_when_ordinary_cannot_leave_a_keeper(fakes):
    teachers = [Teacher.create("Short", teacher_id="short")]
    matcher = make_matcher(
        fakes,
        teachers,
        fixed={(0, 1): ["short"]},
        short={(0, 1): ["short"]},
    )

    result = matcher.select_candidate("2026-09-21", 0, 1)

    assert result.source_type is SubstitutionSourceType.SHORT_TERM_SUBSTITUTION
    assert result.substitute.id == "short"
    assert result.staff_room_keeper is None
