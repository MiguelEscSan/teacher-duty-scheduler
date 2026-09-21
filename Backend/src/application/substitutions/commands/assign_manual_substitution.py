from dataclasses import dataclass
from typing import Optional
from sqlmodel import Session, select
from src.application.common.mediator import Command, RequestHandler
from src.domain import Absence, SubstitutionSourceType
from src.infrastructure.db.models import AbsenceDB, SubstitutionLogDB


@dataclass(frozen=True)
class AssignManualSubstitutionCommand(Command[dict]):
    date: str
    period: int
    absent_teacher_id: str
    substitute_teacher_id: str
    group_id: Optional[str] = None
    notes: Optional[str] = "Asignación manual"


class AssignManualSubstitutionHandler(RequestHandler[AssignManualSubstitutionCommand, dict]):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, cmd: AssignManualSubstitutionCommand) -> dict:
        # 1. Obtener o crear la ausencia mediante su entidad de dominio
        absence_record = self.session.exec(
            select(AbsenceDB).where(
                AbsenceDB.date == cmd.date,
                AbsenceDB.period == cmd.period,
                AbsenceDB.teacher_id == cmd.absent_teacher_id,
            )
        ).first()

        if absence_record:
            absence = absence_record.to_domain()
        else:
            absence = Absence.create(
                teacher_id=cmd.absent_teacher_id,
                date=cmd.date,
                period=cmd.period,
                reason="Ausencia reportada en asignación manual",
            )
            absence_record = AbsenceDB(
                id=absence.id,
                teacher_id=absence.teacher_id,
                date=absence.date,
                period=absence.period,
                reason=absence.reason,
            )

        # 2. El dominio resuelve la ausencia y genera el log de auditoría
        sub_log = absence.resolve_with_substitute(
            substitute_teacher_id=cmd.substitute_teacher_id,
            source_type=SubstitutionSourceType.MANUAL,
            group_id=cmd.group_id,
        )

        absence_record.apply_domain(absence)
        self.session.add(absence_record)

        # 3. Guardar log generado por el dominio
        existing_log = self.session.exec(
            select(SubstitutionLogDB).where(
                SubstitutionLogDB.date == cmd.date,
                SubstitutionLogDB.period == cmd.period,
                SubstitutionLogDB.absent_teacher_id == cmd.absent_teacher_id,
            )
        ).first()

        if existing_log:
            existing_log.substitute_teacher_id = sub_log.substitute_teacher_id
            existing_log.source_type = sub_log.source_type
            self.session.add(existing_log)
        else:
            self.session.add(SubstitutionLogDB(
                date=sub_log.date,
                period=sub_log.period,
                absent_teacher_id=sub_log.absent_teacher_id,
                substitute_teacher_id=sub_log.substitute_teacher_id,
                group_id=sub_log.group_id,
                source_type=sub_log.source_type,
            ))

        self.session.commit()
        return {"message": "Sustitución manual asignada correctamente"}