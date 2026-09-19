from typing import Any
from pydantic import BaseModel, Field

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

class ToggleSlotResponse(BaseModel):
    teacher_id: str
    day: int
    period: int
    status: str

class SlotCellResponse(BaseModel):
    day: int
    period: int
    status: str


# --- Ausencias ---
class AbsenceCreate(BaseModel):
    teacher_id: str
    date: str      # Formato ISO "YYYY-MM-DD"
    period: int = Field(ge=0, le=5)
    reason: str = "Permiso / Asunto propio"

class AbsenceResponse(BaseModel):
    teacher_id: str
    teacher_name: str
    week: int
    day: int
    period: int
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