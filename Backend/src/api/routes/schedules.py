from fastapi import APIRouter, Depends, HTTPException
from src.api.dependencies import get_repository
from src.api.schemas import AbsenceCreate, SlotToggleRequest
from src.infrastructure.db.models import AbsenceDB
from src.infrastructure.repositories import SQLGuardRepository

router = APIRouter(prefix="/api", tags=["Schedules & Absences"])


@router.get("/teachers/{teacher_id}/base-schedule")
def get_teacher_base_schedule(teacher_id: str, repo: SQLGuardRepository = Depends(get_repository)):
    if not repo.get_teacher_by_id(teacher_id):
        raise HTTPException(status_code=404, detail="Profesor no encontrado.")

    entries = repo.get_base_schedule_for_teacher(teacher_id)
    status_map = {(e.day, e.period): e.status for e in entries}

    grid = []
    for p in range(6):
        row = []
        for d in range(5):
            st = status_map.get((d, p), "FREE")
            row.append({"day": d, "period": p, "status": st})
        grid.append(row)
    return grid


@router.put("/base-schedule/toggle")
def toggle_base_slot(payload: SlotToggleRequest, repo: SQLGuardRepository = Depends(get_repository)):
    new_status = repo.toggle_base_slot(payload.teacher_id, payload.day, payload.period)
    return {"teacher_id": payload.teacher_id, "day": payload.day, "period": payload.period, "status": new_status}


@router.get("/absences")
def get_absences(repo: SQLGuardRepository = Depends(get_repository)):
    absences = repo.get_all_absences()
    teachers = {t.id: t.name for t in repo.get_all_teachers()}
    return [
        {
            "id": a.id,
            "teacher_id": a.teacher_id,
            "teacher_name": teachers.get(a.teacher_id, a.teacher_id),
            "date": a.date,
            "period": a.period,
            "reason": a.reason
        }
        for a in absences
    ]


@router.post("/absences")
def create_absence(dto: AbsenceCreate, repo: SQLGuardRepository = Depends(get_repository)):
    if not repo.get_teacher_by_id(dto.teacher_id):
        raise HTTPException(status_code=404, detail="Profesor no encontrado.")

    db_item = AbsenceDB(
        teacher_id=dto.teacher_id,
        date=dto.date,
        period=dto.period,
        reason=dto.reason
    )
    return repo.create_absence(db_item)


@router.delete("/absences/{absence_id}")
def delete_absence(absence_id: int, repo: SQLGuardRepository = Depends(get_repository)):
    success = repo.delete_absence(absence_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ausencia no encontrada.")
    return {"message": "Ausencia eliminada con éxito."}