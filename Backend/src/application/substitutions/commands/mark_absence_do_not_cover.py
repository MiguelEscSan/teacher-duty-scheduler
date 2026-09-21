from dataclasses import dataclass
from src.application.common.mediator import Command
from sqlmodel import Session, select
from src.application.common.mediator import RequestHandler
from src.infrastructure.db.models import AbsenceDB


@dataclass(frozen=True)
class MarkAbsenceDoNotCoverCommand(Command[dict]):
    date: str
    period: int
    absent_teacher_id: str


class MarkAbsenceDoNotCoverHandler(
    RequestHandler[MarkAbsenceDoNotCoverCommand, dict]
):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, cmd: MarkAbsenceDoNotCoverCommand) -> dict:
        absence = self.session.exec(
            select(AbsenceDB).where(
                AbsenceDB.date == cmd.date,
                AbsenceDB.period == cmd.period,
                AbsenceDB.teacher_id == cmd.absent_teacher_id,
            )
        ).first()

        if absence is None:
            raise ValueError("Ausencia no encontrada.")

        absence.resolved = True
        self.session.add(absence)
        self.session.commit()
        self.session.refresh(absence)

        return {
            "message": "Ausencia marcada como no cubrir.",
            "resolved": absence.resolved,
        }