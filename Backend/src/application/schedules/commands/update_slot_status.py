from dataclasses import dataclass
from typing import Optional

from src.application.common.mediator import Command, RequestHandler
from src.domain.ports.schedule_repository import ScheduleRepository
from src.domain.schedule import ScheduleEntry, SlotStatus


@dataclass(frozen=True)
class ToggleSlotTypeCommand(Command[dict]):
    teacher_id: str
    day: int
    period: int
    status: str
    group_id: Optional[str] = None


class ToggleSlotTypeHandler(RequestHandler[ToggleSlotTypeCommand, dict]):
    def __init__(self, schedule_repository: ScheduleRepository):
        self.schedule_repository = schedule_repository

    def handle(self, cmd: ToggleSlotTypeCommand) -> dict:
        status = SlotStatus(cmd.status)
        if status == SlotStatus.TEACHING and not cmd.group_id:
            raise ValueError("Una franja lectiva debe tener un grupo.")
        if status != SlotStatus.TEACHING and cmd.group_id is not None:
            raise ValueError("Solo una franja lectiva puede tener un grupo.")

        entry = self.schedule_repository.get_slot(cmd.teacher_id, cmd.day, cmd.period)
        if entry is None:
            entry = ScheduleEntry(
                teacher_id=cmd.teacher_id,
                day_of_week=cmd.day,
                period=cmd.period,
            )
        entry.group_id = cmd.group_id if status == SlotStatus.TEACHING else None
        entry.is_teaching = status == SlotStatus.TEACHING
        entry.slot_type = status.value
        self.schedule_repository.save(entry)
        return {"status": "OK"}
