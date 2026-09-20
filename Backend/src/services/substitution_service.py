from datetime import datetime
from typing import Optional
from sqlmodel import Session, select
from src.infrastructure.db.models import (
    AbsenceDB,
    FixedDutyDB,
    ShortTermSubstitutionDB,
    StudentGroupDB,
    SubstitutionLogDB,
    SubstitutionSourceType,
    TeacherDB,
    TeacherScheduleDB,
)


class SubstitutionService:
    def __init__(self, session: Session):
        self.session = session

    def preview_day_absence(self, teacher_id: str, date_str: str) -> dict:
        """
        Calcula las horas con docencia efectiva frente a alumnos.
        Si hay co-docencia en el aula, marca que ya hay un docente titular presente.
        """
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        day_of_week = date_obj.weekday()

        if day_of_week > 4:
            return {"error": "La fecha seleccionada corresponde a un fin de semana."}

        target_teacher = self.session.get(TeacherDB, teacher_id)
        if not target_teacher:
            return {"error": "Docente no encontrado."}

        # 1. Obtener franjas donde el profesor tiene grupo asignado (clase con alumnos)
        teaching_slots = self.session.exec(
            select(TeacherScheduleDB).where(
                TeacherScheduleDB.teacher_id == teacher_id,
                TeacherScheduleDB.day_of_week == day_of_week,
                TeacherScheduleDB.is_teaching == True,
                TeacherScheduleDB.group_id.is_not(None),
            )
        ).all()

        periods_to_cover = []
        for slot in sorted(teaching_slots, key=lambda s: s.period):
            group = self.session.get(StudentGroupDB, slot.group_id)
            group_name = group.name if group else "Grupo Desconocido"
            group_students = group.student_count if group else None

            # 2. Detección de Co-docencia / Asignaturas compartidas
            co_teachers = self.session.exec(
                select(TeacherScheduleDB).where(
                    TeacherScheduleDB.day_of_week == day_of_week,
                    TeacherScheduleDB.period == slot.period,
                    TeacherScheduleDB.group_id == slot.group_id,
                    TeacherScheduleDB.teacher_id != teacher_id,
                )
            ).all()

            active_co_teacher = None
            if co_teachers:
                # Comprobar si el co-docente no está ausente ese mismo día y hora
                for ct in co_teachers:
                    ct_absence = self.session.exec(
                        select(AbsenceDB).where(
                            AbsenceDB.teacher_id == ct.teacher_id,
                            AbsenceDB.date == date_str,
                            AbsenceDB.period == slot.period,
                        )
                    ).first()
                    if not ct_absence:
                        t_obj = self.session.get(TeacherDB, ct.teacher_id)
                        active_co_teacher = t_obj.name if t_obj else ct.teacher_id
                        break

            periods_to_cover.append({
                "period": slot.period,
                "group_id": slot.group_id,
                "group_name": group_name,
                "student_count": group_students,
                "has_co_teacher": active_co_teacher is not None,
                "co_teacher_name": active_co_teacher,
                "requires_action": active_co_teacher is None,
            })

        return {
            "teacher_id": teacher_id,
            "teacher_name": target_teacher.name,
            "date": date_str,
            "day_of_week": day_of_week,
            "slots": periods_to_cover,
        }

    def _get_active_absent_teacher_ids(self, date_str: str, period: int) -> set[str]:
        absences = self.session.exec(
            select(AbsenceDB.teacher_id).where(
                AbsenceDB.date == date_str, AbsenceDB.period == period
            )
        ).all()
        return set(absences)

    def _get_least_recently_used(
            self, candidate_ids: list[str], period: int
    ) -> Optional[str]:
        """
        Selecciona al docente cuya última intervención en esta franja sea la más antigua.
        Si nunca intervino, tiene máxima prioridad.
        """
        if not candidate_ids:
            return None

        # Historial de intervenciones en este periodo
        logs = self.session.exec(
            select(SubstitutionLogDB)
            .where(
                SubstitutionLogDB.substitute_teacher_id.in_(candidate_ids),
                SubstitutionLogDB.period == period,
            )
            .order_by(SubstitutionLogDB.created_at.desc())
        ).all()

        last_used_map: dict[str, datetime] = {}
        for log in logs:
            if log.substitute_teacher_id not in last_used_map:
                last_used_map[log.substitute_teacher_id] = log.created_at

        never_used = [cid for cid in candidate_ids if cid not in last_used_map]
        if never_used:
            return never_used[0]

        return min(last_used_map, key=lambda cid: last_used_map[cid])

    def find_ordinary_guard_substitute(
            self, date_str: str, day_of_week: int, period: int
    ) -> tuple[Optional[TeacherDB], Optional[TeacherDB], str]:
        """
        Regla de la Sala de Profesores:
        Total disponibles = N.
        Para poder salir al aula debe haber al menos 2 profesores (N >= 2).
        1 se queda obligatoriamente en la sala de profesores.
        Devuelve: (sustituto_aula, profesor_en_sala, mensaje_estado)
        """
        fixed_duties = self.session.exec(
            select(FixedDutyDB).where(
                FixedDutyDB.day_of_week == day_of_week,
                FixedDutyDB.period == period,
            )
        ).all()
        candidate_ids = [fd.teacher_id for fd in fixed_duties]

        absent_ids = self._get_active_absent_teacher_ids(date_str, period)
        # Quitar ausentes y los que ya estén asignados a cubrir otra aula en ese mismo periodo hoy
        busy_logs = self.session.exec(
            select(SubstitutionLogDB.substitute_teacher_id).where(
                SubstitutionLogDB.date == date_str,
                SubstitutionLogDB.period == period,
            )
        ).all()
        unavailable_ids = absent_ids.union(set(busy_logs))

        available_candidate_ids = [cid for cid in candidate_ids if cid not in unavailable_ids]
        n_available = len(available_candidate_ids)

        if n_available < 2:
            return (
                None,
                self.session.get(TeacherDB, available_candidate_ids[0]) if n_available == 1 else None,
                "Sin cupo de guardia ordinaria: Se requiere mínimo 1 profesor permanente en Sala de Profesores.",
            )

        # Seleccionar por rotación para salir al aula
        chosen_id = self._get_least_recently_used(available_candidate_ids, period)
        remaining_ids = [cid for cid in available_candidate_ids if cid != chosen_id]

        # El profesor que se queda en la sala es cualquiera de los que restan
        staff_room_teacher = self.session.get(TeacherDB, remaining_ids[0])
        chosen_teacher = self.session.get(TeacherDB, chosen_id)

        return (chosen_teacher, staff_room_teacher, "Asignado desde guardia ordinaria.")

    def find_short_term_substitute(
            self, date_str: str, day_of_week: int, period: int
    ) -> tuple[Optional[TeacherDB], str]:
        """Busca en la lista estipulada de sustitución corta mediante turno rotativo propio."""
        entries = self.session.exec(
            select(ShortTermSubstitutionDB).where(
                ShortTermSubstitutionDB.day_of_week == day_of_week,
                ShortTermSubstitutionDB.period == period,
            )
        ).all()
        candidate_ids = [e.teacher_id for e in entries]

        absent_ids = self._get_active_absent_teacher_ids(date_str, period)
        busy_logs = self.session.exec(
            select(SubstitutionLogDB.substitute_teacher_id).where(
                SubstitutionLogDB.date == date_str,
                SubstitutionLogDB.period == period,
            )
        ).all()
        unavailable = absent_ids.union(set(busy_logs))

        available = [cid for cid in candidate_ids if cid not in unavailable]
        if not available:
            return None, "Lista de sustitución corta agotada o no disponible."

        chosen_id = self._get_least_recently_used(available, period)
        return self.session.get(TeacherDB, chosen_id), "Asignado por lista de sustitución corta."

    def register_log(
            self,
            date_str: str,
            period: int,
            absent_teacher_id: str,
            substitute_teacher_id: str,
            group_id: Optional[str],
            source: SubstitutionSourceType,
    ) -> SubstitutionLogDB:
        log = SubstitutionLogDB(
            date=date_str,
            period=period,
            absent_teacher_id=absent_teacher_id,
            substitute_teacher_id=substitute_teacher_id,
            group_id=group_id,
            source_type=source,
        )
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log