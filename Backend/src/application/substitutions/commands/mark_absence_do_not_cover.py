from dataclasses import dataclass

from src.application.common.mediator import Command, RequestHandler
from src.domain.ports.absence_repository import AbsenceRepository


@dataclass(frozen=True)
class MarkAbsenceDoNotCoverCommand(Command[dict]):
    date: str
    period: int
    absent_teacher_id: str


class MarkAbsenceDoNotCoverHandler(RequestHandler[MarkAbsenceDoNotCoverCommand, dict]):
    def __init__(self, absence_repository: AbsenceRepository):
        self.absence_repository = absence_repository

    def handle(self, cmd: MarkAbsenceDoNotCoverCommand) -> dict:
        absence = self.absence_repository.get_by_slot(
            cmd.absent_teacher_id, cmd.date, cmd.period
        )
        if absence is None:
            raise ValueError("Ausencia no encontrada.")
        absence.mark_as_do_not_cover()
        self.absence_repository.save(absence)
        return {"message": "Ausencia marcada como no cubrir.", "resolved": absence.resolved}
