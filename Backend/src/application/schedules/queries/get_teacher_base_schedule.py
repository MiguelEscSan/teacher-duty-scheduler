from dataclasses import dataclass
from src.application.common.mediator import Query
from typing import Any
from sqlmodel import Session, select
from src.application.common.mediator import RequestHandler
from src.infrastructure.db.models import StudentGroupDB, TeacherDB, TeacherScheduleDB

@dataclass(frozen=True)
class GetTeacherBaseScheduleQuery(Query[list[list[dict[str, Any]]]]):
    teacher_id: str

class GetTeacherBaseScheduleHandler(
    RequestHandler[GetTeacherBaseScheduleQuery, list[list[dict[str, Any]]]]
):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, query: GetTeacherBaseScheduleQuery) -> list[list[dict[str, Any]]]:
        if not self.session.get(TeacherDB, query.teacher_id):
            raise ValueError("Profesor no encontrado.")

        entries = self.session.exec(
            select(TeacherScheduleDB).where(
                TeacherScheduleDB.teacher_id == query.teacher_id
            )
        ).all()

        groups = {g.id: g.name for g in self.session.exec(select(StudentGroupDB)).all()}

        slot_map: dict[tuple[int, int], dict[str, Any]] = {}
        for e in entries:
            if e.is_teaching and e.group_id:
                slot_map[(e.day_of_week, e.period)] = {
                    "status": "TEACHING",
                    "group_id": e.group_id,
                    "group_name": groups.get(e.group_id, e.group_id),
                }
            else:
                slot_map[(e.day_of_week, e.period)] = {
                    "status": "FREE",
                    "group_id": None,
                    "group_name": None,
                }

        grid: list[list[dict[str, Any]]] = []
        for p in range(6):
            row = []
            for d in range(5):
                info = slot_map.get(
                    (d, p),
                    {"status": "FREE", "group_id": None, "group_name": None},
                )
                row.append({
                    "day": d,
                    "period": p,
                    "status": info["status"],
                    "group_id": info["group_id"],
                    "group_name": info["group_name"],
                })
            grid.append(row)

        return grid