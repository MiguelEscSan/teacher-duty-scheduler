# src/application/queries/get_available_candidates/query.py
from dataclasses import dataclass
from src.api.schemas import AvailableTeacherOut
from src.application.common.mediator import Query
from datetime import datetime
from sqlmodel import Session, func, select

from src.api.schemas import AvailableTeacherOut
from src.application.common.mediator import RequestHandler
from src.infrastructure.db.models import (
    AbsenceDB,
    FixedDutyDB,
    ShortTermSubstitutionDB,
    SubstitutionLogDB,
    TeacherDB,
    TeacherScheduleDB,
)

@dataclass(frozen=True)
class GetAvailableCandidatesQuery(Query[list[AvailableTeacherOut]]):
    date_str: str
    period: int


class GetAvailableCandidatesHandler(
    RequestHandler[GetAvailableCandidatesQuery, list[AvailableTeacherOut]]
):
    def __init__(self, session: Session):
        self.session = session

    def handle(self, request: GetAvailableCandidatesQuery) -> list[AvailableTeacherOut]:
        target_date = datetime.strptime(request.date_str, "%Y-%m-%d").date()
        day_of_week = target_date.weekday()  # 0: Lunes, 4: Viernes

        # Regla de dominio: fuera de días lectivos no hay candidatos
        if day_of_week > 4:
            return []

        # 1. Conjunto de IDs bloqueados: ausentes ese día y periodo
        absent_ids = set(
            self.session.exec(
                select(AbsenceDB.teacher_id).where(
                    AbsenceDB.date == request.date_str,
                    AbsenceDB.period == request.period,
                )
            ).all()
        )

        # 2. Conjunto de IDs bloqueados: ya asignados a otra sustitución en este periodo
        busy_ids = set(
            self.session.exec(
                select(SubstitutionLogDB.substitute_teacher_id).where(
                    SubstitutionLogDB.date == request.date_str,
                    SubstitutionLogDB.period == request.period,
                )
            ).all()
        )

        # 3. Conjunto de IDs bloqueados: clase lectiva propia frente a alumnos
        teaching_ids = set(
            self.session.exec(
                select(TeacherScheduleDB.teacher_id).where(
                    TeacherScheduleDB.day_of_week == day_of_week,
                    TeacherScheduleDB.period == request.period,
                    TeacherScheduleDB.is_teaching == True,
                )
            ).all()
        )

        unavailable_ids = absent_ids | busy_ids | teaching_ids

        # 4. Docentes con Guardia Ordinaria Fija en esta franja
        fixed_duties = set(
            self.session.exec(
                select(FixedDutyDB.teacher_id).where(
                    FixedDutyDB.day_of_week == day_of_week,
                    FixedDutyDB.period == request.period,
                )
            ).all()
        )

        # 5. Docentes en lista de Sustitución Corta en esta franja
        short_term_duties = set(
            self.session.exec(
                select(ShortTermSubstitutionDB.teacher_id).where(
                    ShortTermSubstitutionDB.day_of_week == day_of_week,
                    ShortTermSubstitutionDB.period == request.period,
                )
            ).all()
        )

        # 6. Conteo agregado de intervenciones (evita el query N+1 original en bucle)
        intervention_counts = dict(
            self.session.exec(
                select(
                    SubstitutionLogDB.substitute_teacher_id,
                    func.count(SubstitutionLogDB.id),
                ).group_by(SubstitutionLogDB.substitute_teacher_id)
            ).all()
        )

        # 7. Obtener profesores no bloqueados y clasificarlos
        all_teachers = self.session.exec(select(TeacherDB)).all()
        candidates: list[AvailableTeacherOut] = []

        for teacher in all_teachers:
            if teacher.id in unavailable_ids:
                continue

            # Categorización del tipo de guardia
            if teacher.id in fixed_duties:
                duty_type = "FIXED_DUTY"
            elif teacher.id in short_term_duties:
                duty_type = "SHORT_TERM"
            else:
                duty_type = "FREE"

            candidates.append(
                AvailableTeacherOut(
                    id=teacher.id,
                    name=teacher.name,
                    department=teacher.department,
                    duty_type=duty_type,
                    interventions_count=intervention_counts.get(teacher.id, 0),
                )
            )

        # Ordenar: primero guardia fija (0), luego corta (1), luego libres (2), seguido de carga acumulada y nombre
        order_priority = {"FIXED_DUTY": 0, "SHORT_TERM": 1, "FREE": 2}
        candidates.sort(
            key=lambda c: (
                order_priority[c.duty_type],
                c.interventions_count,
                c.name.lower(),
            )
        )

        return candidates