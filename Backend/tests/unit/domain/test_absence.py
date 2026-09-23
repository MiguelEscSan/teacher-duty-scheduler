import pytest

from src.domain.absence import Absence
from src.domain.exceptions.absence_already_resolved_exception import AbsenceAlreadyResolvedException
from src.domain.exceptions.invalid_operation_exception import InvalidOperationException
from src.domain.substitution import SubstitutionSourceType


@pytest.mark.unit
def test_absence_transitions_to_resolved_without_substitute():
    absence = Absence.create("teacher-1", "2026-09-21", 2)

    absence.mark_as_do_not_cover()

    assert absence.resolved is True


@pytest.mark.unit
def test_absence_resolves_with_substitute_and_creates_log():
    absence = Absence.create("teacher-1", "2026-09-21", 2)

    log = absence.resolve_with_substitute("teacher-2", SubstitutionSourceType.ORDINARY_GUARD)

    assert absence.resolved is True
    assert log.absent_teacher_id == "teacher-1"
    assert log.substitute_teacher_id == "teacher-2"


@pytest.mark.unit
def test_resolving_an_already_resolved_absence_is_rejected():
    absence = Absence.create("teacher-1", "2026-09-21", 2)
    absence.mark_as_do_not_cover()

    with pytest.raises(AbsenceAlreadyResolvedException):
        absence.resolve_by_excursion()


@pytest.mark.unit
@pytest.mark.parametrize("period", [-1, 6])
def test_absence_rejects_period_outside_school_range(period):
    with pytest.raises(InvalidOperationException):
        Absence.create("teacher-1", "2026-09-21", period)
