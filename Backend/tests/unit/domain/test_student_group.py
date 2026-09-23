import pytest

from src.domain.exceptions.domain_exception import CapacityExceededException
from src.domain.student_group import StudentGroup


@pytest.mark.unit
def test_student_groups_merge_and_accumulate_students():
    first = StudentGroup.create("1A", student_count=15, max_capacity=40)
    second = StudentGroup.create("1B", student_count=20, max_capacity=40)

    merged = first.merge_with(second)

    assert merged is first
    assert merged.student_count == 35


@pytest.mark.unit
def test_student_groups_reject_merge_over_capacity():
    first = StudentGroup.create("1A", student_count=25, max_capacity=40)
    second = StudentGroup.create("1B", student_count=16, max_capacity=40)

    with pytest.raises(CapacityExceededException):
        first.merge_with(second)
