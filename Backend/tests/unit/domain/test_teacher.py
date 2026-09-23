import pytest

from src.domain.exceptions.invalid_operation_exception import InvalidOperationException
from src.domain.teacher import CorporateEmail, Teacher


@pytest.mark.unit
def test_corporate_email_normalizes_accented_teacher_name():
    email = CorporateEmail.from_teacher_name("López Gómez, Eva")

    assert email.email == "lopez@centroeducativo.es"


@pytest.mark.unit
@pytest.mark.parametrize("name", ["", "A", "   "])
def test_teacher_create_rejects_empty_or_too_short_name(name):
    with pytest.raises(InvalidOperationException):
        Teacher.create(name)


@pytest.mark.unit
def test_teacher_create_generates_id_and_corporate_email():
    teacher = Teacher.create("Eva López")

    assert teacher.id
    assert teacher.email.email == "eva@centroeducativo.es"
