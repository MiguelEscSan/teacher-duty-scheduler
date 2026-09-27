from typing import Any
from pydantic import BaseModel, Field
from enum import Enum
from typing import Literal, Optional
from datetime import datetime
from src.domain.duty_type import DutyType

# --- Docentes ---
class TeacherCreate(BaseModel):
    name: str = Field(min_length=2, description="Nombre completo del profesor")
    department: str = Field(
        default="General", description="Departamento al que pertenece"
    )

class TeacherResponse(BaseModel):
    id: str  # GUID devuelto al cliente
    name: str
    department: str

# --- Horario Base ---
class SlotToggleRequest(BaseModel):
    teacher_id: str  # GUID del profesor
    day: int = Field(ge=0, le=4)
    period: int = Field(ge=0, le=5)
    group_id: Optional[str] = None  # None = Libre, string = ID o Nombre del Grupo


class SlotStatusUpdateRequest(BaseModel):
    teacher_id: str
    day: int = Field(ge=0, le=4)
    period: int = Field(ge=0, le=5)
    status: Literal["FREE", "NON_PRESENTIAL", "TEACHING"]
    group_id: Optional[str] = None

class ToggleSlotResponse(BaseModel):
    teacher_id: str
    day: int
    period: int
    status: str

class SlotCellResponse(BaseModel):
    day: int
    period: int
    status: str


class StudentGroupResponse(BaseModel):
    id: str
    name: str
    student_count: Optional[int] = None

StudentGroupResponseDto = StudentGroupResponse


class StudentGroupCreate(BaseModel):
    name: str = Field(
        min_length=1, max_length=50,
        description="Nombre único del grupo (ej. 1ºA_ESO)",
    )
    student_count: Optional[int] = Field(
        default=None, ge=0, description="Número de alumnos asignados al aula"
    )


class StudentGroupUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=50, description="Nuevo nombre del grupo")
    student_count: Optional[int] = Field(
        default=None, ge=0, description="Nuevo número de alumnos"
    )


# --- Ausencias ---
class AbsenceCreate(BaseModel):
    teacher_id: str
    date: str      # Formato ISO "YYYY-MM-DD"
    all_day: bool = False
    period: Optional[int] = Field(default=None, ge=0, le=5)
    reason: str = "Permiso / Asunto propio"

class AbsenceResponse(BaseModel):
    id: str
    teacher_id: str
    teacher_name: str
    date: str
    period: int
    resolved: bool
    group_id: Optional[str] = None
    group_name: str
    student_count: Optional[int] = None
    reason: str

# --- Optimizacion ---
class OptimizeRequest(BaseModel):
    start_date: str

class OptimizationResult(BaseModel):
    status: str
    is_optimal: bool
    total_deficits: int
    max_difference: int
    weeks: list[dict[str, Any]]
    ranking: list[dict[str, Any]]

class ResolutionAction(str, Enum):
    AUTO_ASSIGN = "AUTO_ASSIGN"          # Intentar guardia ordinaria; si no, escalar a corta
    EXCURSION = "EXCURSION"              # Marcar resuelto sin sustitución por excursión del grupo
    MERGE_GROUPS = "MERGE_GROUPS"        # Fusión manual con otro grupo simultáneo
    FORCE_SHORT_TERM = "FORCE_SHORT_TERM"# Escalar directamente a sustitución corta

class PeriodResolveRequest(BaseModel):
    date: str
    period: int
    absent_teacher_id: str
    group_id: Optional[str] = None
    action: ResolutionAction = ResolutionAction.AUTO_ASSIGN
    merged_with_group_id: Optional[str] = None  # ID de la clase con la que se fusiona


class SubstitutionEmailRequest(BaseModel):
    date: str
    period: int = Field(ge=0, le=5)
    absent_teacher_id: str
    substitute_teacher_id: str
    group_id: Optional[str] = None


class PeriodResolveResponse(BaseModel):
    date: str
    period: int
    resolved: bool
    action_applied: str
    substitute_id: Optional[str] = None
    substitute_name: Optional[str] = None
    substitute_email: Optional[str] = None
    source_type: Optional[str] = None
    is_short_term_substitute: bool = False
    is_fixed_duty_substitute: bool = False
    staff_room_keeper_name: Optional[str] = None
    email_notification_dispatched: bool = False
    details: str

class AvailableTeacherOut(BaseModel):
    id: str
    name: str
    department: str
    duty_type: str  # 'FIXED_DUTY' (guardia ordinaria), 'SHORT_TERM' (sustitución corta), o 'FREE' (hora libre)
    interventions_count: int  # Para que jefatura vea cuántas sustituciones lleva este curso


class DutySlotOut(BaseModel):
    day_of_week: int
    day_name: str
    period: int
    teachers: list[TeacherResponse]


class DutyAssignmentRequest(BaseModel):
    teacher_id: str
    day_of_week: int = Field(ge=0, le=4, description="0: Lunes ... 4: Viernes")
    period: int = Field(ge=0, le=5, description="0 a 5")
    duty_type: DutyType


class DutyAssignmentResponse(BaseModel):
    message: str
    teacher_id: str
    day_of_week: int
    period: int
    duty_type: DutyType

class ManualAssignmentIn(BaseModel):
    date: str  # 'YYYY-MM-DD'
    period: int  # 0 a 5
    absent_teacher_id: str
    substitute_teacher_id: str
    group_id: Optional[str] = None
    notes: Optional[str] = "Asignación manual"


class SubstitutionHistoryOut(BaseModel):
    id: str
    date: str
    period: int
    substitute_teacher_id: str
    substitute_teacher_name: str
    absent_teacher_id: str
    absent_teacher_name: str
    group_id: Optional[str] = None
    group_name: Optional[str] = None
    source_type: str
    created_at: datetime


class SubstitutionInterventionsSummaryOut(BaseModel):
    teacher_id: str
    teacher_name: str
    ordinary_guard_count: int
    short_term_count: int
    manual_count: int
    total_interventions: int


class ReassignSubstituteRequest(BaseModel):
    new_substitute_teacher_id: str


class ReassignSubstituteResponse(BaseModel):
    id: str
    date: str
    period: int
    absent_teacher_id: str
    substitute_teacher_id: str
    source_type: str
    absent_teacher_name: str
    substitute_teacher_name: str
    message: str = "Sustituto reasignado correctamente."


class DoNotCoverRequest(BaseModel):
    date: str
    period: int = Field(ge=0, le=5)
    absent_teacher_id: str


class DutyCoverageItem(BaseModel):
    period: int
    covered: bool
    substitute_teacher_id: str | None = None
    substitute_teacher_name: str | None = None
    message: str


class AutoCoverDutiesResponse(BaseModel):
    teacher_id: str
    teacher_name: str
    date: str
    total_duties_found: int
    successfully_covered: int
    uncovered_duties: int
    coverages: list[DutyCoverageItem]
    alerts: list[str]