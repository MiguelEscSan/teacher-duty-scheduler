from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.api.schemas import PeriodResolveResponse, ResolutionAction
from src.application.common.mediator import Command, RequestHandler
from src.domain.absence import Absence
from src.domain.ports.absence_repository import AbsenceRepository
from src.domain.ports.schedule_repository import ScheduleRepository
from src.domain.ports.student_group_repository import StudentGroupRepository
from src.domain.repositories import SubstitutionRepository
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
    ):
        self.teacher_repository = teacher_repository
        self.absence_repository = absence_repository
        self.schedule_repository = schedule_repository
        self.substitution_repository = substitution_repository
        self.student_group_repository = student_group_repository

    def _available_ids(self, date: str, period: int, ids: list[str]) -> list[str]:
        absent = {
            item.teacher_id
            for item in self.absence_repository.get_all(date=date)
            if item.period == period
        }
        busy = self.substitution_repository.get_busy_teacher_ids(date, period)
        return [item for item in ids if item not in absent and item not in busy]

    def _choose(self, ids: list[str], period: int) -> str | None:
        if not ids:
            return None
        last_used = self.substitution_repository.get_last_used_at(ids, period)
        never_used = [item for item in ids if item not in last_used]
        return never_used[0] if never_used else min(last_used, key=last_used.get)

    def _ordinary(self, date: str, day: int, period: int):
        available = self._available_ids(
            date, period,
            self.schedule_repository.get_fixed_duty_teacher_ids(day, period),
        )
        if len(available) < 2:
            keeper = self.teacher_repository.get_by_id(available[0]) if available else None
            return None, keeper, (
                "Sin cupo de guardia ordinaria: Se requiere mínimo 1 profesor permanente "
                "en Sala de Profesores."
            )
        chosen = self._choose(available, period)
        keeper_id = next(item for item in available if item != chosen)
        return (
            self.teacher_repository.get_by_id(chosen),
            self.teacher_repository.get_by_id(keeper_id),
            "Asignado desde guardia ordinaria.",
        )

    def _short_term(self, date: str, day: int, period: int):
        available = self._available_ids(
            date, period,
            self.schedule_repository.get_short_term_teacher_ids(day, period),
        )
        if not available:
            return None, "Lista de sustitución corta agotada o no disponible."
        return (
            self.teacher_repository.get_by_id(self._choose(available, period)),
            "Asignado por lista de sustitución corta.",
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
        substitute = None
        staff_room_keeper = None
        source = None
        details = ""
        if cmd.action == ResolutionAction.AUTO_ASSIGN:
            substitute, staff_room_keeper, details = self._ordinary(
                cmd.date, day_of_week, cmd.period
            )
            if substitute:
                source = SubstitutionSourceType.ORDINARY_GUARD
        if not substitute or cmd.action == ResolutionAction.FORCE_SHORT_TERM:
            substitute, details = self._short_term(cmd.date, day_of_week, cmd.period)
            if substitute:
                source = SubstitutionSourceType.SHORT_TERM_SUBSTITUTION
            else:
                return PeriodResolveResponse(
                    date=cmd.date, period=cmd.period, resolved=False,
                    action_applied=cmd.action.value,
                    details="ALERTA: Sin profesores disponibles en guardia ni en sustitución corta.",
                )
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
