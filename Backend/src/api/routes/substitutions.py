from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlmodel import Session
from src.api.dependencies import get_session
from src.api.schemas import (
    TeacherResponse,
    AvailableTeacherOut,
    DutySlotOut,
    ManualAssignmentIn,
    PeriodResolveRequest,
    PeriodResolveResponse,
    ResolutionAction,
    SubstitutionEmailRequest,
)
from src.infrastructure.db.models import AbsenceDB, StudentGroupDB, SubstitutionSourceType, TeacherDB, \
    SubstitutionLogDB, FixedDutyDB, ShortTermSubstitutionDB, TeacherScheduleDB
from src.services.email_service import send_urgent_substitution_email
from src.services.substitution_service import SubstitutionService
from sqlmodel import Session, select
from typing import List

router = APIRouter(prefix="/api/v1/substitutions", tags=["Sustituciones Operativas"])
DAY_NAMES = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes")


@router.get("/duty-teachers", response_model=List[DutySlotOut])
def get_duty_teachers(
    day_of_week: int | None = Query(default=None, ge=0, le=4),
    period: int | None = Query(default=None, ge=0, le=5),
    session: Session = Depends(get_session),
):
    """Devuelve el calendario semanal de profesores con guardia fija."""
    duty_query = select(FixedDutyDB)
    if day_of_week is not None:
        duty_query = duty_query.where(FixedDutyDB.day_of_week == day_of_week)
    if period is not None:
        duty_query = duty_query.where(FixedDutyDB.period == period)

    duties = session.exec(duty_query).all()
    teacher_ids = {duty.teacher_id for duty in duties}
    teachers = {
        teacher.id: teacher
        for teacher in session.exec(
            select(TeacherDB).where(TeacherDB.id.in_(teacher_ids))
        ).all()
    }

    teachers_by_slot: dict[tuple[int, int], list[TeacherResponse]] = {}
    for duty in duties:
        teacher = teachers.get(duty.teacher_id)
        if teacher is None:
            continue

        teachers_by_slot.setdefault((duty.day_of_week, duty.period), []).append(
            TeacherResponse(
                id=teacher.id,
                name=teacher.name,
                department=teacher.department,
            ),
        )

    days = [day_of_week] if day_of_week is not None else range(5)
    periods = [period] if period is not None else range(6)
    return [
        DutySlotOut(
            day_of_week=day,
            day_name=DAY_NAMES[day],
            period=slot_period,
            teachers=sorted(
                teachers_by_slot.get((day, slot_period), []),
                key=lambda teacher: teacher.name.lower(),
            ),
        )
        for day in days
        for slot_period in periods
    ]


@router.get("/short-term-teachers", response_model=List[DutySlotOut])
def get_short_term_teachers(
    day_of_week: int | None = Query(default=None, ge=0, le=4),
    period: int | None = Query(default=None, ge=0, le=5),
    session: Session = Depends(get_session),
):
    """Devuelve el calendario semanal de profesores de sustitución corta."""
    substitution_query = select(ShortTermSubstitutionDB)
    if day_of_week is not None:
        substitution_query = substitution_query.where(
            ShortTermSubstitutionDB.day_of_week == day_of_week
        )
    if period is not None:
        substitution_query = substitution_query.where(
            ShortTermSubstitutionDB.period == period
        )

    substitutions = session.exec(substitution_query).all()
    teacher_ids = {substitution.teacher_id for substitution in substitutions}
    teachers = {
        teacher.id: teacher
        for teacher in session.exec(
            select(TeacherDB).where(TeacherDB.id.in_(teacher_ids))
        ).all()
    }

    teachers_by_slot: dict[tuple[int, int], list[TeacherResponse]] = {}
    for substitution in substitutions:
        teacher = teachers.get(substitution.teacher_id)
        if teacher is None:
            continue

        teachers_by_slot.setdefault(
            (substitution.day_of_week, substitution.period), []
        ).append(
            TeacherResponse(
                id=teacher.id,
                name=teacher.name,
                department=teacher.department,
            )
        )

    days = [day_of_week] if day_of_week is not None else range(5)
    periods = [period] if period is not None else range(6)
    return [
        DutySlotOut(
            day_of_week=day,
            day_name=DAY_NAMES[day],
            period=slot_period,
            teachers=sorted(
                teachers_by_slot.get((day, slot_period), []),
                key=lambda teacher: teacher.name.lower(),
            ),
        )
        for day in days
        for slot_period in periods
    ]


@router.post("/resolve", response_model=PeriodResolveResponse)
def resolve_substitution(
    payload: PeriodResolveRequest,
    session: Session = Depends(get_session),
):
    service = SubstitutionService(session)
    date_obj = datetime.strptime(payload.date, "%Y-%m-%d").date()
    day_of_week = date_obj.weekday()

    absent_teacher = session.get(TeacherDB, payload.absent_teacher_id)
    if not absent_teacher:
        raise HTTPException(status_code=404, detail="Profesor ausente no encontrado.")

    group = session.get(StudentGroupDB, payload.group_id) if payload.group_id else None
    group_name = group.name if group else "Sin Grupo"

    # Registrar la ausencia en la BD si aún no consta
    existing_absence = session.query(AbsenceDB).filter_by(
        teacher_id=payload.absent_teacher_id,
        date=payload.date,
        period=payload.period
    ).first()
    if not existing_absence:
        session.add(
            AbsenceDB(
                teacher_id=payload.absent_teacher_id,
                date=payload.date,
                period=payload.period,
                reason="Ausencia reportada en despacho",
            )
        )
        session.commit()

    # Caso 1: Excursión
    if payload.action == ResolutionAction.EXCURSION:
        return PeriodResolveResponse(
            date=payload.date,
            period=payload.period,
            resolved=True,
            action_applied=ResolutionAction.EXCURSION.value,
            details=f"Grupo [{group_name}] en excursión. No se requiere sustituto.",
        )

    # Caso 2: Fusión Manual de Clases
    if payload.action == ResolutionAction.MERGE_GROUPS:
        target_group = session.get(StudentGroupDB, payload.merged_with_group_id)
        target_name = target_group.name if target_group else "otro grupo"
        target_count = target_group.student_count if target_group and target_group.student_count is not None else 0
        current_count = group.student_count if group and group.student_count is not None else 0

        return PeriodResolveResponse(
            date=payload.date,
            period=payload.period,
            resolved=True,
            action_applied=ResolutionAction.MERGE_GROUPS.value,
            details=(
                f"Fusión manual: [{group_name}] ({current_count} alum.) integrado en "
                f"[{target_name}] ({target_count} alum.). Total aprox: {current_count + target_count} alumnos."
            ),
        )

    # Caso 3: Asignación Operativa (Guardia Ordinaria o Sustitución Corta)
    substitute = None
    source = None
    staff_room_keeper = None
    details = ""

    if payload.action == ResolutionAction.AUTO_ASSIGN:
        substitute, staff_room_keeper, details = service.find_ordinary_guard_substitute(
            payload.date, day_of_week, payload.period
        )
        if substitute:
            source = SubstitutionSourceType.ORDINARY_GUARD

    # Si no hubo cupo ordinario (o se fuerza explícitamente), escalar a Sustitución Corta
    if not substitute or payload.action == ResolutionAction.FORCE_SHORT_TERM:
        substitute, details = service.find_short_term_substitute(
            payload.date, day_of_week, payload.period
        )
        if substitute:
            source = SubstitutionSourceType.SHORT_TERM_SUBSTITUTION
        else:
            return PeriodResolveResponse(
                date=payload.date,
                period=payload.period,
                resolved=False,
                action_applied=payload.action.value,
                details="ALERTA: Sin profesores disponibles en guardia ni en sustitución corta.",
            )

    # Registrar en el histórico de rotación
    service.register_log(
        date_str=payload.date,
        period=payload.period,
        absent_teacher_id=payload.absent_teacher_id,
        substitute_teacher_id=substitute.id,
        group_id=payload.group_id,
        source=source,
    )

    return PeriodResolveResponse(
        date=payload.date,
        period=payload.period,
        resolved=True,
        action_applied=source.value,
        substitute_id=substitute.id,
        substitute_name=substitute.name,
        substitute_email=substitute.email,
        source_type=source.value,
        is_short_term_substitute=source == SubstitutionSourceType.SHORT_TERM_SUBSTITUTION,
        is_fixed_duty_substitute=source == SubstitutionSourceType.ORDINARY_GUARD,
        staff_room_keeper_name=staff_room_keeper.name if staff_room_keeper else None,
        details=details,
    )


@router.post("/send-email")
def send_substitution_email(
    payload: SubstitutionEmailRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    """Envía la notificación de una sustitución ya asignada."""
    absent_teacher = session.get(TeacherDB, payload.absent_teacher_id)
    if absent_teacher is None:
        raise HTTPException(status_code=404, detail="Profesor ausente no encontrado.")

    substitute = session.get(TeacherDB, payload.substitute_teacher_id)
    if substitute is None:
        raise HTTPException(status_code=404, detail="Profesor sustituto no encontrado.")

    assignment = session.exec(
        select(SubstitutionLogDB).where(
            SubstitutionLogDB.date == payload.date,
            SubstitutionLogDB.period == payload.period,
            SubstitutionLogDB.absent_teacher_id == payload.absent_teacher_id,
            SubstitutionLogDB.substitute_teacher_id == payload.substitute_teacher_id,
        )
    ).first()
    if assignment is None:
        raise HTTPException(
            status_code=404,
            detail="No existe una sustitución asignada con esos datos.",
        )

    group = session.get(StudentGroupDB, payload.group_id) if payload.group_id else None
    group_name = group.name if group else "Sin Grupo"
    background_tasks.add_task(
        send_urgent_substitution_email,
        to_email=substitute.email,
        teacher_name=substitute.name,
        group_name=group_name,
        period=payload.period,
        date_str=payload.date,
        absent_teacher_name=absent_teacher.name,
    )
    return {"message": "Correo de sustitución programado correctamente."}


@router.get("/available-candidates", response_model=List[AvailableTeacherOut])
def get_available_candidates(date_str: str, period: int, session: Session = Depends(get_session)):
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    day_of_week = target_date.weekday()  # 0: Lunes, 4: Viernes

    if day_of_week > 4:
        return []

    # 1. Profesores que faltan ese día y periodo
    absent_teacher_ids = set(
        session.exec(
            select(AbsenceDB.teacher_id).where(
                AbsenceDB.date == date_str,
                AbsenceDB.period == period
            )
        ).all()
    )

    # 2. Profesores que ya están ocupados cubriendo otra aula en este periodo
    already_substituting_ids = set(
        session.exec(
            select(SubstitutionLogDB.substitute_teacher_id).where(
                SubstitutionLogDB.date == date_str,
                SubstitutionLogDB.period == period
            )
        ).all()
    )

    # 3. Profesores con clase lectiva propia frente a alumnos
    teaching_teacher_ids = set(
        session.exec(
            select(TeacherScheduleDB.teacher_id).where(
                TeacherScheduleDB.day_of_week == day_of_week,
                TeacherScheduleDB.period == period,
                TeacherScheduleDB.is_teaching == True
            )
        ).all()
    )

    unavailable_ids = absent_teacher_ids | already_substituting_ids | teaching_teacher_ids

    # 4. Docentes con Guardia Ordinaria Fija en esta franja
    fixed_duties = session.exec(
        select(FixedDutyDB.teacher_id).where(
            FixedDutyDB.day_of_week == day_of_week,
            FixedDutyDB.period == period
        )
    ).all()
    fixed_duty_set = set(fixed_duties)

    # 5. Docentes en lista de Sustitución Corta
    short_term = session.exec(
        select(ShortTermSubstitutionDB.teacher_id).where(
            ShortTermSubstitutionDB.day_of_week == day_of_week,
            ShortTermSubstitutionDB.period == period
        )
    ).all()
    short_term_set = set(short_term)

    # 6. Obtener todos los profesores que no estén bloqueados
    all_teachers = session.exec(select(TeacherDB)).all()
    candidates = []

    for t in all_teachers:
        if t.id in unavailable_ids:
            continue

        # Categorizar
        if t.id in fixed_duty_set:
            duty_type = "FIXED_DUTY"
        elif t.id in short_term_set:
            duty_type = "SHORT_TERM"
        else:
            duty_type = "FREE"

        # Conteo de intervenciones para dar contexto a jefatura
        count = len(session.exec(
            select(SubstitutionLogDB).where(SubstitutionLogDB.substitute_teacher_id == t.id)
        ).all())

        candidates.append(AvailableTeacherOut(
            id=t.id,
            name=t.name,
            department=t.department,
            duty_type=duty_type,
            interventions_count=count
        ))

    # Ordenar: primero los de guardia ordinaria, luego sustitución corta, luego libres
    order_priority = {"FIXED_DUTY": 0, "SHORT_TERM": 1, "FREE": 2}
    candidates.sort(key=lambda c: (order_priority[c.duty_type], c.interventions_count, c.name))

    return candidates


@router.post("/assign-manual", status_code=status.HTTP_201_CREATED)
def assign_manual_substitution(payload: ManualAssignmentIn, session: Session = Depends(get_session)):
    # Comprobar si ya estaba cubierto
    existing = session.exec(
        select(SubstitutionLogDB).where(
            SubstitutionLogDB.date == payload.date,
            SubstitutionLogDB.period == payload.period,
            SubstitutionLogDB.absent_teacher_id == payload.absent_teacher_id
        )
    ).first()

    if existing:
        # Si ya existe, actualizamos el sustituto
        existing.substitute_teacher_id = payload.substitute_teacher_id
        existing.source_type = "MANUAL"
        session.add(existing)
    else:
        new_log = SubstitutionLogDB(
            date=payload.date,
            period=payload.period,
            absent_teacher_id=payload.absent_teacher_id,
            substitute_teacher_id=payload.substitute_teacher_id,
            group_id=payload.group_id,
            source_type="MANUAL"
        )
        session.add(new_log)

    session.commit()
    return {"message": "Sustitución manual asignada correctamente"}