from dataclasses import asdict, dataclass
from datetime import datetime

from src.domain.ports.absence_repository import AbsenceRepository
from src.domain.ports.schedule_repository import ScheduleRepository
from src.domain.ports.substitution_repository import SubstitutionRepository
from src.domain.ports.teacher_repository import TeacherRepository
from src.domain.substitution import SubstitutionSourceType
from src.domain.teacher import Teacher


@dataclass(frozen=True)
class CandidateSelection:
    substitute: Teacher | None
    staff_room_keeper: Teacher | None
    source_type: SubstitutionSourceType | None
    reason: str


@dataclass(frozen=True)
class DutyCoverage:
    period: int
    covered: bool
    substitute_teacher_id: str | None
    substitute_teacher_name: str | None
    message: str


class AutoCoverTeacherDutiesService:
    def __init__(
        self,
        teacher_repository: TeacherRepository,
        absence_repository: AbsenceRepository,
        schedule_repository: ScheduleRepository,
        substitution_repository: SubstitutionRepository,
    ):
        self.teacher_repository = teacher_repository
        self.absence_repository = absence_repository
        self.schedule_repository = schedule_repository
        self.substitution_repository = substitution_repository

    def select_candidate(
        self,
        date: str,
        day_of_week: int,
        period: int,
        force_short_term: bool = False,
    ) -> CandidateSelection:
        if not force_short_term:
            ordinary = self._ordinary(date, day_of_week, period)
            if ordinary.substitute is not None:
                return ordinary

        short_term, reason = self._short_term(date, day_of_week, period)
        if short_term is None:
            return CandidateSelection(None, None, None, reason)
        return CandidateSelection(
            short_term,
            None,
            SubstitutionSourceType.SHORT_TERM_SUBSTITUTION,
            reason,
        )

    def _available_ids(self, date: str, period: int, ids: list[str]) -> list[str]:
        absent = {
            item.teacher_id
            for item in self.absence_repository.get_all(date=date)
            if item.period == period
        }
        busy = self.substitution_repository.get_busy_teacher_ids(date, period)
        return [
            teacher_id
            for teacher_id in ids
            if teacher_id not in absent and teacher_id not in busy
        ]

    def _choose(self, teacher_ids: list[str], period: int) -> str | None:
        if not teacher_ids:
            return None
        last_used = self.substitution_repository.get_last_used_at(
            teacher_ids, period
        )
        never_used = [
            teacher_id for teacher_id in teacher_ids if teacher_id not in last_used
        ]
        return never_used[0] if never_used else min(last_used, key=last_used.get)

    def _ordinary(
        self, date: str, day_of_week: int, period: int
    ) -> CandidateSelection:
        available = self._available_ids(
            date,
            period,
            self.schedule_repository.get_fixed_duty_teacher_ids(day_of_week, period),
        )
        if len(available) < 2:
            keeper = (
                self.teacher_repository.get_by_id(available[0])
                if available
                else None
            )
            return CandidateSelection(
                None,
                keeper,
                None,
                "Sin cupo de guardia ordinaria: Se requiere mínimo 1 profesor permanente "
                "en Sala de Profesores.",
            )

        chosen_id = self._choose(available, period)
        keeper_id = next(
            teacher_id for teacher_id in available if teacher_id != chosen_id
        )
        return CandidateSelection(
            self.teacher_repository.get_by_id(chosen_id),
            self.teacher_repository.get_by_id(keeper_id),
            SubstitutionSourceType.ORDINARY_GUARD,
            "Asignado desde guardia ordinaria.",
        )

    def _short_term(
        self, date: str, day_of_week: int, period: int
    ) -> tuple[Teacher | None, str]:
        available = self._available_ids(
            date,
            period,
            self.schedule_repository.get_short_term_teacher_ids(day_of_week, period),
        )
        if not available:
            return None, "Lista de sustitución corta agotada o no disponible."
        chosen_id = self._choose(available, period)
        return (
            self.teacher_repository.get_by_id(chosen_id),
            "Asignado por lista de sustitución corta.",
        )

    def cover(self, teacher_id: str, date: str, periods: list[int]) -> dict:
        teacher = self.teacher_repository.get_by_id(teacher_id)
        if teacher is None:
            raise ValueError("Profesor no encontrado.")

        day_of_week = datetime.strptime(date, "%Y-%m-%d").weekday()
        assigned_coverages = [
            log
            for log in self.substitution_repository.get_all(
                date=date, substitute_teacher_id=teacher_id
            )
            if log.period in periods and log.group_id is None
        ]
        assigned_coverages.sort(key=lambda log: log.period)
        duty_periods = sorted(
            period
            for period in {log.period for log in assigned_coverages}
        )
        alerts: list[str] = []
        coverages: list[DutyCoverage] = []

        for log in assigned_coverages:
            period = log.period
            match = self.select_candidate(
                date, day_of_week, period
            )
            candidate = match.substitute
            source_type = match.source_type
            if candidate is None or source_type is None:
                message = (
                    f"ALERTA CRÍTICA: En el Periodo P{period} no hay docentes disponibles "
                    "para cubrir la guardia de retén. Requiere intervención manual urgente."
                )
                alerts.append(message)
                coverages.append(DutyCoverage(period, False, None, None, message))
                continue

            log.substitute_teacher_id = candidate.id
            log.source_type = source_type
            self.substitution_repository.save(log)
            message = f"Periodo P{period}: Asignado automáticamente a {candidate.name}."
            alerts.append(message)
            coverages.append(
                DutyCoverage(period, True, candidate.id, candidate.name, message)
            )

        covered = sum(item.covered for item in coverages)
        return {
            "teacher_id": teacher.id,
            "teacher_name": teacher.name,
            "date": date,
            "total_duties_found": len(duty_periods),
            "successfully_covered": covered,
            "uncovered_duties": len(coverages) - covered,
            "coverages": [asdict(item) for item in coverages],
            "alerts": alerts,
        }
