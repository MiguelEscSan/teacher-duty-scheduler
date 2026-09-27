import pytest

from src.domain.schedule import ScheduleSlot, SlotStatus, TeacherSchedule, TimeSlot


def test_non_presential_slot_is_not_available():
    schedule = TeacherSchedule("teacher-1")
    slot = TimeSlot("2026-09-21", 0, 1)
    schedule.slots[slot.date, slot.period] = SlotStatus.NON_PRESENTIAL

    assert schedule.is_available(slot) is False


def test_schedule_slot_can_be_marked_non_presential():
    slot = ScheduleSlot(TimeSlot("2026-09-21", 0, 1))

    slot.mark_as_non_presential()

    assert slot.status == SlotStatus.NON_PRESENTIAL
    assert slot.assigned_group is None


def test_releasing_slot_accepts_free_or_non_presential():
    slot = ScheduleSlot(TimeSlot("2026-09-21", 0, 1))

    slot.release_to_free(SlotStatus.NON_PRESENTIAL)

    assert slot.status == SlotStatus.NON_PRESENTIAL

    with pytest.raises(Exception):
        slot.release_to_free(SlotStatus.TEACHING)
