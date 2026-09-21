from datetime import datetime
from typing import Optional

from src.domain.repositories.absence_repository import AbsenceRepository
from src.domain.repositories.schedule_repository import ScheduleRepository
from src.domain.repositories.student_group_repository import StudentGroupRepository
from src.domain.repositories.substitution_repository import SubstitutionRepository
from src.domain.repositories.teacher_repository import TeacherRepository
from src.domain.substitution import SubstitutionLog, SubstitutionSourceType


class SubstitutionService:
    """Domain use-case service backed exclusively by repository ports."""

    def __init__(
        self,
        teacher_repository: TeacherRepository,
        absence_repository: AbsenceRepository,
        schedule_repository: ScheduleRepository,
        substitution_repository: SubstitutionRepository,
        student_group_repository: StudentGroupRepository | None = None,
    ):
        self.teacher_repository = teacher_repository
        self.absence_repository = absence_repository
        self.schedule_repository = schedule_repository
        self.substitution_repository = substitution_repository
        self.student_group_repository = student_group_repository

    def preview_day_absence(self, teacher_id: str, date_str: str) -> dict:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        day_of_week = date_obj.weekday()
        if day_of_week > 4:
            return {"error": "La fecha seleccionada corresponde a un fin de semana."}
        target = self.teacher_repository.get_by_id(teacher_id)
        if not target:
            return {"error": "Docente no encontrado."}
        groups = {
            g.id: g for g in self.student_group_repository.get_all()
        } if self.student_group_repository else {}
        entries = [
            entry for entry in self.schedule_repository.get_for_teacher(teacher_id)
            if entry.day_of_week == day_of_week and entry.is_teaching and entry.group_id
        ]
        result = []
        for entry in sorted(entries, key=lambda item: item.period):
            group = groups.get(entry.group_id)
            co_teacher_name = None
            for other in self.schedule_repository.get_all():
                if (
                    other.teacher_id != teacher_id
                    and other.day_of_week == day_of_week
                    and other.period == entry.period
                    and other.group_id == entry.group_id
                    and not self.absence_repository.get_by_slot(
                        other.teacher_id, date_str, entry.period
                    )
                ):
                    co_teacher = self.teacher_repository.get_by_id(other.teacher_id)
                    co_teacher_name = co_teacher.name if co_teacher else other.teacher_id
                    break
            result.append({
                "period": entry.period,
                "group_id": entry.group_id,
                "group_name": group.name if group else "Grupo Desconocido",
                "student_count": group.student_count if group else None,
                "has_co_teacher": co_teacher_name is not None,
                "co_teacher_name": co_teacher_name,
                "requires_action": co_teacher_name is None,
            })
        return {
            "teacher_id": teacher_id,
            "teacher_name": target.name,
            "date": date_str,
            "day_of_week": day_of_week,
            "slots": result,
        }

    def _get_active_absent_teacher_ids(self, date_str: str, period: int) -> set[str]:
        return {
            item.teacher_id
            for item in self.absence_repository.get_all(date=date_str)
            if item.period == period
        }

    def _get_least_recently_used(self, candidate_ids: list[str], period: int) -> str | None:
        if not candidate_ids:
            return None
        last_used = self.substitution_repository.get_last_used_at(candidate_ids, period)
        never_used = [item for item in candidate_ids if item not in last_used]
        return never_used[0] if never_used else min(last_used, key=last_used.get)

    def find_ordinary_guard_substitute(
        self, date_str: str, day_of_week: int, period: int
    ) -> tuple[object | None, object | None, str]:
        candidate_ids = self.schedule_repository.get_fixed_duty_teacher_ids(day_of_week, period)
        unavailable = self._get_active_absent_teacher_ids(date_str, period)
        unavailable |= self.substitution_repository.get_busy_teacher_ids(date_str, period)
        available = [item for item in candidate_ids if item not in unavailable]
        if len(available) < 2:
            keeper = self.teacher_repository.get_by_id(available[0]) if len(available) == 1 else None
            return None, keeper, (
                "Sin cupo de guardia ordinaria: Se requiere mínimo 1 profesor permanente "
                "en Sala de Profesores."
            )
        chosen_id = self._get_least_recently_used(available, period)
        remaining = [item for item in available if item != chosen_id]
        return (
            self.teacher_repository.get_by_id(chosen_id),
            self.teacher_repository.get_by_id(remaining[0]),
            "Asignado desde guardia ordinaria.",
        )

    def find_short_term_substitute(
        self, date_str: str, day_of_week: int, period: int
    ) -> tuple[object | None, str]:
        candidate_ids = self.schedule_repository.get_short_term_teacher_ids(day_of_week, period)
        unavailable = self._get_active_absent_teacher_ids(date_str, period)
        unavailable |= self.substitution_repository.get_busy_teacher_ids(date_str, period)
        available = [item for item in candidate_ids if item not in unavailable]
        if not available:
            return None, "Lista de sustitución corta agotada o no disponible."
        chosen = self._get_least_recently_used(available, period)
        return self.teacher_repository.get_by_id(chosen), "Asignado por lista de sustitución corta."

    def register_log(
        self,
        date_str: str,
        period: int,
        absent_teacher_id: str,
        substitute_teacher_id: str,
        group_id: Optional[str],
        source: SubstitutionSourceType,
    ) -> SubstitutionLog:
        return self.substitution_repository.save(
            SubstitutionLog.create(
                date=date_str,
                period=period,
                absent_teacher_id=absent_teacher_id,
                substitute_teacher_id=substitute_teacher_id,
                group_id=group_id,
                source_type=source,
            )
        )
