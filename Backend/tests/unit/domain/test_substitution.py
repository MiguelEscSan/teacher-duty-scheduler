import pytest

from src.domain.exceptions.invalid_operation_exception import InvalidOperationException
from src.domain.substitution import SubstitutionLog, SubstitutionSourceType


@pytest.mark.unit
def test_substitution_log_rejects_self_substitution():
    with pytest.raises(InvalidOperationException):
        SubstitutionLog.create(
            "2026-09-21", 0, "teacher-1", "teacher-1",
            SubstitutionSourceType.MANUAL,
        )


@pytest.mark.unit
def test_substitution_log_factory_generates_uuid_and_keeps_source():
    log = SubstitutionLog.create(
        "2026-09-21", 0, "teacher-1", "teacher-2",
        SubstitutionSourceType.MANUAL,
    )

    assert len(log.id) == 36
    assert log.source_type is SubstitutionSourceType.MANUAL
