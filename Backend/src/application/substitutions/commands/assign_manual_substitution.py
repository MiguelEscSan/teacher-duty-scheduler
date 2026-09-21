from dataclasses import dataclass
from typing import Optional

from src.application.common.mediator import Command, RequestHandler
from src.domain.absence import Absence
from src.domain.repositories.absence_repository import AbsenceRepository
from src.domain.repositories.substitution_repository import SubstitutionRepository
from src.domain.substitution import SubstitutionSourceType


@dataclass(frozen=True)
class AssignManualSubstitutionCommand(Command[dict]):
    date: str
    period: int
    absent_teacher_id: str
    substitute_teacher_id: str
    group_id: Optional[str] = None
    notes: Optional[str] = "Asignación manual"


class AssignManualSubstitutionHandler(RequestHandler[AssignManualSubstitutionCommand, dict]):
    def __init__(
        self,
        absence_repository: AbsenceRepository,
        substitution_repository: SubstitutionRepository,
    ):
        self.absence_repository = absence_repository
        self.substitution_repository = substitution_repository

    def handle(self, cmd: AssignManualSubstitutionCommand) -> dict:
        absence = self.absence_repository.get_by_slot(
            cmd.absent_teacher_id, cmd.date, cmd.period
        )
        if absence is None:
            absence = Absence.create(
                teacher_id=cmd.absent_teacher_id,
                date=cmd.date,
                period=cmd.period,
                reason="Ausencia reportada en asignación manual",
            )
        log = absence.resolve_with_substitute(
            cmd.substitute_teacher_id, SubstitutionSourceType.MANUAL, cmd.group_id
        )
        self.absence_repository.save(absence)
        existing = self.substitution_repository.get_all(
            date=cmd.date, absent_teacher_id=cmd.absent_teacher_id
        )
        if existing:
            existing[0].substitute_teacher_id = log.substitute_teacher_id
            existing[0].group_id = log.group_id
            existing[0].source_type = log.source_type
            self.substitution_repository.save(existing[0])
        else:
            self.substitution_repository.save(log)
        return {"message": "Sustitución manual asignada correctamente"}
