from datetime import datetime
from sqlmodel import Session, select
from src.application.common.mediator import RequestHandler
from src.infrastructure.db.models import AbsenceDB, TeacherDB
from dataclasses import dataclass
from typing import Optional
from src.application.common.mediator import Command


@dataclass(frozen=True)
class CreateAbsenceCommand(Command[dict]):
    teacher_id: str
    date: str
    all_day: bool = False
    period: Optional[int] = None
    reason: str = "Permiso / Asunto propio"

class CreateAbsenceHandler(RequestHandler[CreateAbsenceCommand, dict]):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, cmd: CreateAbsenceCommand) -> dict:
        if not self.session.get(TeacherDB, cmd.teacher_id):
            raise ValueError("Profesor no encontrado.")

        try:
            date_obj = datetime.strptime(cmd.date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Formato de fecha inválido. Usa YYYY-MM-DD.")

        if date_obj.weekday() > 4:
            raise ValueError("La fecha seleccionada no es un día lectivo (lunes a viernes).")

        periods_to_register = list(range(6)) if cmd.all_day else ([cmd.period] if cmd.period is not None else [])
        if not periods_to_register:
            raise ValueError("Debes indicar un periodo o marcar 'Todo el día'.")

        for p in periods_to_register:
            existing = self.session.exec(
                select(AbsenceDB).where(
                    AbsenceDB.teacher_id == cmd.teacher_id,
                    AbsenceDB.date == cmd.date,
                    AbsenceDB.period == p,
                )
            ).first()

            if not existing:
                new_absence = AbsenceDB(
                    teacher_id=cmd.teacher_id,
                    date=cmd.date,
                    period=p,
                    reason=cmd.reason,
                )
                self.session.add(new_absence)

        self.session.commit()
        return {
            "message": "Ausencias registradas correctamente",
            "count": len(periods_to_register),
        }