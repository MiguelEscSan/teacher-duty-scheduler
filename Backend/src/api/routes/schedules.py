from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from src.api.dependencies import get_repository
from src.api.schemas import AbsenceCreate, SlotToggleRequest, AbsenceResponse
from src.api.dependencies import get_session
from src.infrastructure.db.models import StudentGroupDB, TeacherDB, TeacherScheduleDB, AbsenceDB
from src.infrastructure.repositories import SQLGuardRepository

router = APIRouter(prefix="/api", tags=["Schedules & Absences"])


@router.get("/teachers/{teacher_id}/base-schedule")
def get_teacher_base_schedule(teacher_id: str, session: Session = Depends(get_session)):
    if not session.get(TeacherDB, teacher_id):
        raise HTTPException(status_code=404, detail="Profesor no encontrado.")

    entries = session.exec(
        select(TeacherScheduleDB).where(TeacherScheduleDB.teacher_id == teacher_id)
    ).all()

    # Mapeo de grupos para tener nombres legibles
    groups = {g.id: g.name for g in session.exec(select(StudentGroupDB)).all()}

    # Mapa (day, period) -> (status, group_id, group_name)
    slot_map = {}
    for e in entries:
        if e.is_teaching and e.group_id:
            slot_map[(e.day_of_week, e.period)] = {
                "status": "TEACHING",
                "group_id": e.group_id,
                "group_name": groups.get(e.group_id, e.group_id)
            }
        else:
            slot_map[(e.day_of_week, e.period)] = {
                "status": "FREE",
                "group_id": None,
                "group_name": None
            }

    grid = []
    for p in range(6):
        row = []
        for d in range(5):
            info = slot_map.get((d, p), {"status": "FREE", "group_id": None, "group_name": None})
            row.append({
                "day": d,
                "period": p,
                "status": info["status"],
                "group_id": info["group_id"],
                "group_name": info["group_name"]
            })
        grid.append(row)
    return grid

@router.get("/groups")
def get_student_groups(session: Session = Depends(get_session)):
    """Devuelve la lista de grupos disponibles para el selector."""
    return session.exec(select(StudentGroupDB)).all()


@router.put("/base-schedule/assign-slot")
def assign_slot_group(payload: SlotToggleRequest, session: Session = Depends(get_session)):
    entry = session.exec(
        select(TeacherScheduleDB).where(
            TeacherScheduleDB.teacher_id == payload.teacher_id,
            TeacherScheduleDB.day_of_week == payload.day,
            TeacherScheduleDB.period == payload.period
        )
    ).first()

    if payload.group_id is None:
        # Liberar celda
        if entry:
            entry.is_teaching = False
            entry.group_id = None
            session.add(entry)
    else:
        # Asignar grupo y marcar lectivo
        if entry:
            entry.is_teaching = True
            entry.group_id = payload.group_id
            session.add(entry)
        else:
            entry = TeacherScheduleDB(
                teacher_id=payload.teacher_id,
                day_of_week=payload.day,
                period=payload.period,
                group_id=payload.group_id,
                is_teaching=True
            )
            session.add(entry)

    session.commit()
    return {"status": "OK"}



@router.get("/absences", response_model=list[AbsenceResponse])
def get_actionable_absences(session: Session = Depends(get_session)):
    """
    Devuelve exclusivamente las ausencias que requieren sustitución en aula:
    aquellas donde el docente tenía un grupo lectivo asignado en su horario base.
    """
    absences = session.exec(select(AbsenceDB)).all()
    teachers = {t.id: t.name for t in session.exec(select(TeacherDB)).all()}
    groups = {g.id: g for g in session.exec(select(StudentGroupDB)).all()}

    # Mapeo de horarios base: (teacher_id, day_of_week, period) -> schedule
    schedules = session.exec(
        select(TeacherScheduleDB).where(
            TeacherScheduleDB.is_teaching == True,
            TeacherScheduleDB.group_id.is_not(None)
        )
    ).all()
    teaching_map = {(s.teacher_id, s.day_of_week, s.period): s.group_id for s in schedules}

    results = []
    for a in absences:
        try:
            day_of_week = datetime.strptime(a.date, "%Y-%m-%d").weekday()
        except ValueError:
            continue

        # Comprobar si el profesor tenía grupo lectivo en este periodo y día
        group_id = teaching_map.get((a.teacher_id, day_of_week, a.period))
        if group_id:
            group_obj = groups.get(group_id)
            group_name = group_obj.name if group_obj else "Grupo asignado"
            student_count = group_obj.student_count if group_obj else None

            results.append(
                AbsenceResponse(
                    id=a.id,
                    teacher_id=a.teacher_id,
                    teacher_name=teachers.get(a.teacher_id, a.teacher_id),
                    date=a.date,
                    period=a.period,
                    group_name=group_name,
                    student_count=student_count,
                    reason=a.reason,
                )
            )

    # Ordenar por fecha y periodo
    results.sort(key=lambda x: (x.date, x.period))
    return results


@router.post("/absences")
def create_absence(dto: AbsenceCreate, session: Session = Depends(get_session)):
    if not session.get(TeacherDB, dto.teacher_id):
        raise HTTPException(status_code=404, detail="Profesor no encontrado.")

    try:
        date_obj = datetime.strptime(dto.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa YYYY-MM-DD.")

    if date_obj.weekday() > 4:
        raise HTTPException(status_code=400, detail="La fecha seleccionada no es un día lectivo (lunes a viernes).")

    # Si es todo el día, registrar los 6 periodos (0 a 5); si no, solo el indicado
    periods_to_register = list(range(6)) if dto.all_day else ([dto.period] if dto.period is not None else [])

    if not periods_to_register:
        raise HTTPException(status_code=400, detail="Debes indicar un periodo o marcar 'Todo el día'.")

    created_ids = []
    for p in periods_to_register:
        existing = session.exec(
            select(AbsenceDB).where(
                AbsenceDB.teacher_id == dto.teacher_id,
                AbsenceDB.date == dto.date,
                AbsenceDB.period == p,
            )
        ).first()

        if not existing:
            new_absence = AbsenceDB(
                teacher_id=dto.teacher_id,
                date=dto.date,
                period=p,
                reason=dto.reason,
            )
            session.add(new_absence)
            session.commit()
            session.refresh(new_absence)
            created_ids.append(new_absence.id)

    return {"message": "Ausencias registradas correctamente", "count": len(periods_to_register)}


@router.delete("/absences/{absence_id}")
def delete_absence(absence_id: int, repo: SQLGuardRepository = Depends(get_repository)):
    success = repo.delete_absence(absence_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ausencia no encontrada.")
    return {"message": "Ausencia eliminada con éxito."}