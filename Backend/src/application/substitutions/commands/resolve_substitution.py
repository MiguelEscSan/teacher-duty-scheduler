from dataclasses import dataclass
from typing import Optional
from src.api.schemas import PeriodResolveResponse, ResolutionAction
from src.application.common.mediator import Command
from datetime import datetime
from sqlmodel import Session
from src.api.schemas import PeriodResolveResponse, ResolutionAction
from src.application.common.mediator import RequestHandler
from src.domain import SubstitutionSourceType
from src.infrastructure.db.models import AbsenceDB, StudentGroupDB, TeacherDB
from src.services.substitution_service import SubstitutionService

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
    def __init__(self, session: Session):
        self.session = session
        self.service = SubstitutionService(session)

    def handle(self, cmd: ResolveSubstitutionCommand) -> PeriodResolveResponse:
        date_obj = datetime.strptime(cmd.date, "%Y-%m-%d").date()
        day_of_week = date_obj.weekday()

        absent_teacher = self.session.get(TeacherDB, cmd.absent_teacher_id)
        if not absent_teacher:
            raise ValueError(f"Profesor ausente {cmd.absent_teacher_id} no encontrado.")

        group = self.session.get(StudentGroupDB, cmd.group_id) if cmd.group_id else None
        group_name = group.name if group else "Sin Grupo"

        # 1. Asegurar registro de ausencia
        absence = self.session.query(AbsenceDB).filter_by(
            teacher_id=cmd.absent_teacher_id,
            date=cmd.date,
            period=cmd.period
        ).first()
        if not absence:
            absence = AbsenceDB(
                teacher_id=cmd.absent_teacher_id,
                date=cmd.date,
                period=cmd.period,
                reason="Ausencia reportada en despacho",
            )
            self.session.add(absence)
            self.session.commit()

        # 2. Excursión
        if cmd.action == ResolutionAction.EXCURSION:
            absence.resolved = True
            self.session.add(absence)
            self.session.commit()
            return PeriodResolveResponse(
                date=cmd.date,
                period=cmd.period,
                resolved=True,
                action_applied=ResolutionAction.EXCURSION.value,
                details=f"Grupo [{group_name}] en excursión. No se requiere sustituto.",
            )

        # 3. Fusión Manual de Clases
        if cmd.action == ResolutionAction.MERGE_GROUPS:
            target_group = self.session.get(StudentGroupDB, cmd.merged_with_group_id)
            target_name = target_group.name if target_group else "otro grupo"
            target_count = target_group.student_count if target_group and target_group.student_count is not None else 0
            current_count = group.student_count if group and group.student_count is not None else 0

            absence.resolved = True
            self.session.add(absence)
            self.session.commit()
            return PeriodResolveResponse(
                date=cmd.date,
                period=cmd.period,
                resolved=True,
                action_applied=ResolutionAction.MERGE_GROUPS.value,
                details=(
                    f"Fusión manual: [{group_name}] ({current_count} alum.) integrado en "
                    f"[{target_name}] ({target_count} alum.). Total aprox: {current_count + target_count} alumnos."
                ),
            )

        # 4. Asignación Automática / Forzar Corta
        substitute = None
        source = None
        staff_room_keeper = None
        details = ""

        if cmd.action == ResolutionAction.AUTO_ASSIGN:
            substitute, staff_room_keeper, details = self.service.find_ordinary_guard_substitute(
                cmd.date, day_of_week, cmd.period
            )
            if substitute:
                source = SubstitutionSourceType.ORDINARY_GUARD

        if not substitute or cmd.action == ResolutionAction.FORCE_SHORT_TERM:
            substitute, details = self.service.find_short_term_substitute(
                cmd.date, day_of_week, cmd.period
            )
            if substitute:
                source = SubstitutionSourceType.SHORT_TERM_SUBSTITUTION
            else:
                return PeriodResolveResponse(
                    date=cmd.date,
                    period=cmd.period,
                    resolved=False,
                    action_applied=cmd.action.value,
                    details="ALERTA: Sin profesores disponibles en guardia ni en sustitución corta.",
                )

        absence.resolved = True
        self.session.add(absence)
        self.session.commit()

        self.service.register_log(
            date_str=cmd.date,
            period=cmd.period,
            absent_teacher_id=cmd.absent_teacher_id,
            substitute_teacher_id=substitute.id,
            group_id=cmd.group_id,
            source=source,
        )

        return PeriodResolveResponse(
            date=cmd.date,
            period=cmd.period,
            resolved=True,
            action_applied=source.value,
            substitute_id=substitute.id,
            substitute_name=substitute.name,
            substitute_email=substitute.email,
            source_type=source.value,
            is_short_term_substitute=(source == SubstitutionSourceType.SHORT_TERM_SUBSTITUTION),
            is_fixed_duty_substitute=(source == SubstitutionSourceType.ORDINARY_GUARD),
            staff_room_keeper_name=staff_room_keeper.name if staff_room_keeper else None,
            details=details,
        )