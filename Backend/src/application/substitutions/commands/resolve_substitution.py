from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.api.schemas import PeriodResolveResponse, ResolutionAction
from src.application.common.mediator import Command, RequestHandler
from src.application.substitutions.services.auto_cover_teacher_duties import (
    AutoCoverTeacherDutiesService,
)
from src.domain.absence import Absence
from src.domain.ports import SubstitutionRepository
from src.domain.ports.absence_repository import AbsenceRepository
from src.domain.ports.schedule_repository import ScheduleRepository
from src.domain.ports.student_group_repository import StudentGroupRepository
from src.domain.ports.teacher_repository import TeacherRepository
from src.domain.substitution import SubstitutionSourceType


@dataclass(frozen=True)
class ResolveSubstitutionCommand(Command[PeriodResolveResponse]):
    date: str
    period: int
    absent_teacher_id: str
    action: ResolutionAction
    group_id: Optional[str] = None
    merged_with_group_id: Optional[str] = None


class ResolveSubstitutionHandler(
    RequestHandler[ResolveSubstitutionCommand, PeriodResolveResponse]
):
    def __init__(
        self,
        teacher_repository: TeacherRepository,
        absence_repository: AbsenceRepository,
        schedule_repository: ScheduleRepository,
        substitution_repository: SubstitutionRepository,
        student_group_repository: StudentGroupRepository,
        auto_cover_service: AutoCoverTeacherDutiesService | None = None,
    ):
        self.teacher_repository = teacher_repository
        self.absence_repository = absence_repository
        self.schedule_repository = schedule_repository
        self.substitution_repository = substitution_repository
        self.student_group_repository = student_group_repository
        self.auto_cover_service = auto_cover_service or AutoCoverTeacherDutiesService(
            teacher_repository,
            absence_repository,
            schedule_repository,
            substitution_repository,
        )

    def handle(self, cmd: ResolveSubstitutionCommand) -> PeriodResolveResponse:
        day_of_week = datetime.strptime(cmd.date, "%Y-%m-%d").weekday()
        absent_teacher = self.teacher_repository.get_by_id(cmd.absent_teacher_id)
        if not absent_teacher:
            raise ValueError(f"Profesor ausente {cmd.absent_teacher_id} no encontrado.")
        group = (
            self.student_group_repository.get_by_id(cmd.group_id)
            if cmd.group_id else None
        )
        group_name = group.name if group else "Sin Grupo"
        absence = self.absence_repository.get_by_slot(
            cmd.absent_teacher_id, cmd.date, cmd.period
        )
        if absence is None:
            absence = Absence.create(
                cmd.absent_teacher_id, cmd.date, cmd.period,
                "Ausencia reportada en despacho",
            )
            self.absence_repository.save(absence)
        if cmd.action == ResolutionAction.EXCURSION:
            absence.resolve_by_excursion()
            self.absence_repository.save(absence)
            return PeriodResolveResponse(
                date=cmd.date, period=cmd.period, resolved=True,
                action_applied=cmd.action.value,
                details=f"Grupo [{group_name}] en excursión. No se requiere sustituto.",
            )
        if cmd.action == ResolutionAction.MERGE_GROUPS:
            target = (
                self.student_group_repository.get_by_id(cmd.merged_with_group_id)
                if cmd.merged_with_group_id else None
            )
            current_count = group.student_count if group and group.student_count is not None else 0
            target_count = target.student_count if target and target.student_count is not None else 0
            absence.resolve_by_group_merge()
            self.absence_repository.save(absence)
            target_name = target.name if target else "otro grupo"
            return PeriodResolveResponse(
                date=cmd.date, period=cmd.period, resolved=True,
                action_applied=cmd.action.value,
                details=(
                    f"Fusión manual: [{group_name}] ({current_count} alum.) integrado en "
                    f"[{target_name}] ({target_count} alum.). Total aprox: "
                    f"{current_count + target_count} alumnos."
                ),
            )
        match = self.auto_cover_service.select_candidate(
            cmd.date,
            day_of_week,
            cmd.period,
            force_short_term=cmd.action == ResolutionAction.FORCE_SHORT_TERM,
        )
        substitute = match.substitute
        staff_room_keeper = match.staff_room_keeper
        source = match.source_type
        if substitute is None or source is None:
            return PeriodResolveResponse(
                date=cmd.date, period=cmd.period, resolved=False,
                action_applied=cmd.action.value,
                details="ALERTA: Sin profesores disponibles en guardia ni en sustitución corta.",
            )
        details = match.reason
        log = absence.resolve_with_substitute(substitute.id, source, cmd.group_id)
        self.absence_repository.save(absence)
        self.substitution_repository.save(log)
        return PeriodResolveResponse(
            date=cmd.date, period=cmd.period, resolved=True,
            action_applied=source.value, substitute_id=substitute.id,
            substitute_name=substitute.name, substitute_email=str(substitute.email),
            source_type=source.value,
            is_short_term_substitute=source == SubstitutionSourceType.SHORT_TERM_SUBSTITUTION,
            is_fixed_duty_substitute=source == SubstitutionSourceType.ORDINARY_GUARD,
            staff_room_keeper_name=staff_room_keeper.name if staff_room_keeper else None,
            details=details,
        )
