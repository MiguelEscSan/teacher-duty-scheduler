from dataclasses import dataclass
from typing import Optional
from src.application.common.mediator import Command
from sqlmodel import Session, select
from src.application.common.mediator import RequestHandler
from src.infrastructure.db.models import TeacherScheduleDB

@dataclass(frozen=True)
class AssignSlotGroupCommand(Command[dict]):
    teacher_id: str
    day: int
    period: int
    group_id: Optional[str] = None

class AssignSlotGroupHandler(RequestHandler[AssignSlotGroupCommand, dict]):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, cmd: AssignSlotGroupCommand) -> dict:
        entry = self.session.exec(
            select(TeacherScheduleDB).where(
                TeacherScheduleDB.teacher_id == cmd.teacher_id,
                TeacherScheduleDB.day_of_week == cmd.day,
                TeacherScheduleDB.period == cmd.period,
            )
        ).first()

        if cmd.group_id is None:
            if entry:
                entry.is_teaching = False
                entry.group_id = None
                self.session.add(entry)
        else:
            if entry:
                entry.is_teaching = True
                entry.group_id = cmd.group_id
                self.session.add(entry)
            else:
                entry = TeacherScheduleDB(
                    teacher_id=cmd.teacher_id,
                    day_of_week=cmd.day,
                    period=cmd.period,
                    group_id=cmd.group_id,
                    is_teaching=True,
                )
                self.session.add(entry)

        self.session.commit()
        return {"status": "OK"}