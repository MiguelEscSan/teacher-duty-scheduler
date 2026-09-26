from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.application.common.mediator import Command, RequestHandler
from src.domain.absence import Absence
from src.domain.ports.absence_repository import AbsenceRepository
from src.domain.ports.substitution_repository import SubstitutionRepository
from src.domain.ports.teacher_repository import TeacherRepository
from src.domain.substitution import SubstitutionSourceType
from src.application.substitutions.services.auto_cover_teacher_duties import (
    AutoCoverTeacherDutiesService,
)


@dataclass(frozen=True)
class CreateAbsenceCommand(Command[dict]):
    teacher_id: str
    date: str
    all_day: bool = False
    period: Optional[int] = None
    reason: str = "Permiso / Asunto propio"


class CreateAbsenceHandler(RequestHandler[CreateAbsenceCommand, dict]):
    def __init__(
        self,
        absence_repository: AbsenceRepository,
        teacher_repository: TeacherRepository,
        substitution_repository: SubstitutionRepository,
        auto_cover_service: AutoCoverTeacherDutiesService,
    ):
        self.absence_repository = absence_repository
        self.teacher_repository = teacher_repository
        self.substitution_repository = substitution_repository
        self.auto_cover_service = auto_cover_service

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
                self.absence_repository.save(Absence.create(cmd.teacher_id, cmd.date, period, cmd.reason))
        active_duties = [
            log
            for log in self.substitution_repository.get_all(
                date=cmd.date,
                substitute_teacher_id=cmd.teacher_id,
            )
            if (
                log.period in periods
                and log.group_id is None
                and log.source_type
                in (
                    SubstitutionSourceType.ORDINARY_GUARD,
                    SubstitutionSourceType.SHORT_TERM_SUBSTITUTION,
                )
            )
        ]
        result = (
            self.auto_cover_service.cover(cmd.teacher_id, cmd.date, periods)
            if active_duties
            else {
                "teacher_id": cmd.teacher_id,
                "teacher_name": self.teacher_repository.get_by_id(cmd.teacher_id).name,
                "date": cmd.date,
                "total_duties_found": 0,
                "successfully_covered": 0,
                "uncovered_duties": 0,
                "coverages": [],
                "alerts": [],
            }
        )
        return {
            "message": "Ausencias registradas correctamente",
            "count": len(periods),
            **result,
        }
