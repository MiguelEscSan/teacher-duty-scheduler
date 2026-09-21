# src/application/commands/assign_manual_substitution.py
from dataclasses import dataclass
from typing import Optional
from sqlmodel import Session, select
from src.application.common.mediator import Command, RequestHandler
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
        # 1. Registrar o actualizar log de sustitución
        existing = self.session.exec(
            select(SubstitutionLogDB).where(
                SubstitutionLogDB.date == cmd.date,
                SubstitutionLogDB.period == cmd.period,
                SubstitutionLogDB.absent_teacher_id == cmd.absent_teacher_id,
            )
        ).first()

        if existing:
            existing.substitute_teacher_id = cmd.substitute_teacher_id
            existing.source_type = "MANUAL"
            self.session.add(existing)
        else:
            new_log = SubstitutionLogDB(
                date=cmd.date,
                period=cmd.period,
                absent_teacher_id=cmd.absent_teacher_id,
                substitute_teacher_id=cmd.substitute_teacher_id,
                group_id=cmd.group_id,
                source_type="MANUAL",
            )
            self.session.add(new_log)

        # 2. Asegurar y resolver la ausencia
        absence = self.session.exec(
            select(AbsenceDB).where(
                AbsenceDB.date == cmd.date,
                AbsenceDB.period == cmd.period,
                AbsenceDB.teacher_id == cmd.absent_teacher_id,
            )
        ).first()

        if not absence:
            absence = AbsenceDB(
                teacher_id=cmd.absent_teacher_id,
                date=cmd.date,
                period=cmd.period,
                reason="Ausencia reportada en asignación manual",
            )
            self.session.add(absence)

        absence.resolved = True
        self.session.add(absence)
        self.session.commit()

        return {"message": "Sustitución manual asignada correctamente"}