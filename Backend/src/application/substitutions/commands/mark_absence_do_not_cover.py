from dataclasses import dataclass
from sqlmodel import Session, select
from src.application.common.mediator import Command, RequestHandler
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
        absence_record = self.session.exec(
            select(AbsenceDB).where(
                AbsenceDB.date == cmd.date,
                AbsenceDB.period == cmd.period,
                AbsenceDB.teacher_id == cmd.absent_teacher_id,
            )
        ).first()

        if absence_record is None:
            raise ValueError("Ausencia no encontrada.")

        # 1. Hidratar la entidad de dominio
        absence = absence_record.to_domain()

        # 2. Ejecutar la regla de negocio pura
        absence.mark_as_do_not_cover()

        # 3. Persistir los cambios sincronizados
        absence_record.apply_domain(absence)
        self.session.add(absence_record)
        self.session.commit()

        return {
            "message": "Ausencia marcada como no cubrir.",
            "resolved": absence.resolved,
        }