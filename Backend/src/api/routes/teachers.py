from fastapi import APIRouter, Depends, HTTPException
from src.api.dependencies import get_repository
from src.api.schemas import TeacherCreate, TeacherResponse
from src.infrastructure.db.models import TeacherDB
from src.infrastructure.repositories import SQLGuardRepository

router = APIRouter(prefix="/api/teachers", tags=["Teachers"])


@router.get("", response_model=list[TeacherResponse])
def list_teachers(repo: SQLGuardRepository = Depends(get_repository)):
    return repo.get_all_teachers()


@router.post("", response_model=TeacherResponse)
def create_teacher(
    dto: TeacherCreate, repo: SQLGuardRepository = Depends(get_repository)
):
    new_teacher = TeacherDB(name=dto.name, department=dto.department)
    return repo.save_teacher(new_teacher)


@router.delete("/{teacher_id}")
def delete_teacher(
    teacher_id: str, repo: SQLGuardRepository = Depends(get_repository)
):
    success = repo.delete_teacher(teacher_id)
    if not success:
        raise HTTPException(
            status_code=404, detail="Profesor no encontrado."
        )
    return {"message": "Profesor eliminado"}