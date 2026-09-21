from dataclasses import dataclass
from src.application.common.mediator import Command
from sqlmodel import Session, select
from src.application.common.mediator import RequestHandler
from src.infrastructure.db.models import (
    AbsenceDB,
    BaseScheduleDB,
    FixedDutyDB,
    ShortTermSubstitutionDB,
    TeacherDB,
    TeacherScheduleDB,
)

@dataclass(frozen=True)
class DeleteTeacherCommand(Command[bool]):
    teacher_id: str



class DeleteTeacherHandler(RequestHandler[DeleteTeacherCommand, bool]):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, cmd: DeleteTeacherCommand) -> bool:
        teacher = self.session.get(TeacherDB, cmd.teacher_id)
        if not teacher:
            return False

        # Cascada controlada sobre horarios y asignaciones
        for s in self.session.exec(
            select(BaseScheduleDB).where(BaseScheduleDB.teacher_id == cmd.teacher_id)
        ):
            self.session.delete(s)

        for ts in self.session.exec(
            select(TeacherScheduleDB).where(TeacherScheduleDB.teacher_id == cmd.teacher_id)
        ):
            self.session.delete(ts)

        for a in self.session.exec(
            select(AbsenceDB).where(AbsenceDB.teacher_id == cmd.teacher_id)
        ):
            self.session.delete(a)

        for fd in self.session.exec(
            select(FixedDutyDB).where(FixedDutyDB.teacher_id == cmd.teacher_id)
        ):
            self.session.delete(fd)

        for st in self.session.exec(
            select(ShortTermSubstitutionDB).where(ShortTermSubstitutionDB.teacher_id == cmd.teacher_id)
        ):
            self.session.delete(st)

        self.session.delete(teacher)
        self.session.commit()
        return True