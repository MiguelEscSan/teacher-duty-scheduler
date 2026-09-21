from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.application.common.mediator import Command, RequestHandler
from src.domain.absence import Absence
from src.domain.ports.absence_repository import AbsenceRepository
from src.domain.ports.teacher_repository import TeacherRepository


@dataclass(frozen=True)
class CreateAbsenceCommand(Command[dict]):
    teacher_id: str
    date: str
    all_day: bool = False
    period: Optional[int] = None
    reason: str = "Permiso / Asunto propio"


class CreateAbsenceHandler(RequestHandler[CreateAbsenceCommand, dict]):
    def __init__(self, absence_repository: AbsenceRepository, teacher_repository: TeacherRepository):
        self.absence_repository = absence_repository
        self.teacher_repository = teacher_repository

    def handle(self, cmd: CreateAbsenceCommand) -> dict:
        if not self.teacher_repository.get_by_id(cmd.teacher_id):
            raise ValueError("Profesor no encontrado.")
        try:
            date_obj = datetime.strptime(cmd.date, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("Formato de fecha inválido. Usa YYYY-MM-DD.") from exc
        if date_obj.weekday() > 4:
            raise ValueError("La fecha seleccionada no es un día lectivo (lunes a viernes).")
        periods = list(range(6)) if cmd.all_day else ([cmd.period] if cmd.period is not None else [])
        if not periods:
            raise ValueError("Debes indicar un periodo o marcar 'Todo el día'.")
        for period in periods:
            if self.absence_repository.get_by_slot(cmd.teacher_id, cmd.date, period) is None:
                self.absence_repository.save(
                    Absence.create(cmd.teacher_id, cmd.date, period, cmd.reason)
                )
        return {"message": "Ausencias registradas correctamente", "count": len(periods)}
