from datetime import datetime
import uuid
from sqlmodel import Field, SQLModel
from enum import Enum
from typing import Optional


def generate_uuid() -> str:
    return str(uuid.uuid4())


class BaseScheduleDB(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    teacher_id: str = Field(index=True)
    day: int  # 0 a 4
    period: int  # 0 a 5
    status: str  # "FREE" o "TEACHING"

class AbsenceDB(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    teacher_id: str = Field(index=True)
    date: str = Field(index=True)  # "YYYY-MM-DD"
    period: int  # 0 a 5
    reason: str
    resolved: bool = Field(default=False, index=True)

class SubstitutionSourceType(str, Enum):
    ORDINARY_GUARD = "ORDINARY_GUARD"
    SHORT_TERM_SUBSTITUTION = "SHORT_TERM_SUBSTITUTION"


class StudentGroupDB(SQLModel, table=True):
    __tablename__ = "student_groups"

    id: str = Field(default_factory=generate_uuid, primary_key=True)
    name: str = Field(unique=True, index=True)
    student_count: Optional[int] = Field(default=None)

class TeacherDB(SQLModel, table=True):
    __tablename__ = "teachers"

    id: str = Field(default_factory=generate_uuid, primary_key=True)
    name: str
    email: str = Field(default="docente@centro.edu", index=True)
    department: str = Field(default="General", index=True)

class TeacherScheduleDB(SQLModel, table=True):
    __tablename__ = "teacher_schedules"

    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: str = Field(index=True)
    day_of_week: int = Field(index=True)  # 0: Lunes, ..., 4: Viernes
    period: int = Field(index=True)       # 0 a 5
    group_id: Optional[str] = Field(default=None, index=True)  # Si tiene grupo -> Docencia frente a alumnos
    is_teaching: bool = Field(default=True)  # False si es reunión, coordinación o guardia


class FixedDutyDB(SQLModel, table=True):
    """Profesores en guardia ordinaria para una franja semanal concreta."""
    __tablename__ = "fixed_duties"

    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: str = Field(index=True)
    day_of_week: int = Field(index=True)
    period: int = Field(index=True)


class ShortTermSubstitutionDB(SQLModel, table=True):
    """Lista estipulada de sustitución corta para una franja semanal concreta."""
    __tablename__ = "short_term_substitutions"

    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: str = Field(index=True)
    day_of_week: int = Field(index=True)
    period: int = Field(index=True)


class SubstitutionLogDB(SQLModel, table=True):
    """Historial de asignaciones para rotación justa y auditoría."""
    __tablename__ = "substitution_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    date: str = Field(index=True)  # "YYYY-MM-DD"
    period: int = Field(index=True)
    absent_teacher_id: str = Field(index=True)
    substitute_teacher_id: str = Field(index=True)
    group_id: Optional[str] = Field(default=None)
    source_type: SubstitutionSourceType
    created_at: datetime = Field(default_factory=datetime.utcnow)