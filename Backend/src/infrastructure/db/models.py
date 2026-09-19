import uuid
from typing import Optional
from sqlmodel import Field, SQLModel


def generate_uuid() -> str:
    return str(uuid.uuid4())


class TeacherDB(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    name: str
    department: str = Field(default="Sin Asignar", index=True)


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