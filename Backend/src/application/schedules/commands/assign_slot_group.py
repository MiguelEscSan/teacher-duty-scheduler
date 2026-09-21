from dataclasses import dataclass
from typing import Optional

from src.application.common.mediator import Command, RequestHandler
from src.domain.ports.schedule_repository import ScheduleRepository
from src.domain.schedule import ScheduleEntry


@dataclass(frozen=True)
class AssignSlotGroupCommand(Command[dict]):
    teacher_id: str
    day: int
    period: int
    group_id: Optional[str] = None


class AssignSlotGroupHandler(RequestHandler[AssignSlotGroupCommand, dict]):
    def __init__(self, schedule_repository: ScheduleRepository):
        self.schedule_repository = schedule_repository

    def handle(self, cmd: AssignSlotGroupCommand) -> dict:
        entry = self.schedule_repository.get_slot(cmd.teacher_id, cmd.day, cmd.period)
        if entry is None:
            entry = ScheduleEntry(
                teacher_id=cmd.teacher_id,
                day_of_week=cmd.day,
                period=cmd.period,
                group_id=cmd.group_id,
                is_teaching=cmd.group_id is not None,
            )
        else:
            entry.group_id = cmd.group_id
            entry.is_teaching = cmd.group_id is not None
        self.schedule_repository.save(entry)
        return {"status": "OK"}
