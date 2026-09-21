from datetime import datetime, timedelta
from typing import Any

from src.application.common.mediator import Query, RequestHandler
from src.domain.constants import DAYS, PERIODS
from src.domain.guard import AssignmentReport
from src.domain.ports.absence_repository import AbsenceRepository
from src.domain.ports.guard_optimizer import GuardOptimizer
from src.domain.ports.schedule_repository import ScheduleRepository
from src.domain.ports.teacher_repository import TeacherRepository
from src.domain.schedule import SlotStatus, TeacherSchedule, TimeSlot


class CalculateWeekGuardsQuery(Query[dict[str, Any]]):
    def __init__(self, start_date: str):
        self.start_date = start_date


class CalculateWeekGuardsHandler(
    RequestHandler[CalculateWeekGuardsQuery, dict[str, Any]]
):
    def __init__(
        self,
        teacher_repository: TeacherRepository,
        schedule_repository: ScheduleRepository,
        absence_repository: AbsenceRepository,
        optimizer: GuardOptimizer,
    ):
        self.teacher_repository = teacher_repository
        self.schedule_repository = schedule_repository
        self.absence_repository = absence_repository
        self.optimizer = optimizer

    def handle(self, request: CalculateWeekGuardsQuery) -> dict[str, Any]:
        try:
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        except ValueError:
            return {"error": "La fecha debe tener formato YYYY-MM-DD."}

        start_date -= timedelta(days=start_date.weekday())
        week_dates = [start_date + timedelta(days=offset) for offset in range(DAYS)]
        dates_iso = [date.isoformat() for date in week_dates]
        slots = [
            TimeSlot(date=date_str, day_index=day_index, period=period)
            for day_index, date_str in enumerate(dates_iso)
            for period in range(PERIODS)
        ]

        teachers = self.teacher_repository.get_all()
        if not teachers:
            return {"error": "No hay profesores registrados."}

        base_status = {
            (entry.teacher_id, entry.day_of_week, entry.period):
            ("TEACHING" if entry.is_teaching else "FREE")
            for entry in self.schedule_repository.get_all()
        }
        absences = self.absence_repository.get_by_dates(dates_iso)
        absence_slots = {(absence.teacher_id, absence.date, absence.period) for absence in absences}

        schedules: dict[str, TeacherSchedule] = {}
        for teacher in teachers:
            schedule = TeacherSchedule(teacher_id=teacher.id)
            for slot in slots:
                if (teacher.id, slot.date, slot.period) in absence_slots:
                    schedule.slots[slot.date, slot.period] = SlotStatus.ABSENCE
                else:
                    status = base_status.get(
                        (teacher.id, slot.day_index, slot.period), "FREE"
                    )
                    schedule.slots[slot.date, slot.period] = SlotStatus(status)
            schedules[teacher.id] = schedule

        report = self.optimizer.generate_schedule(teachers, slots, schedules)
        return self._format_result(report, teachers, week_dates, dates_iso)

    @staticmethod
    def _format_result(
        report: AssignmentReport,
        teachers: list,
        week_dates: list,
        dates_iso: list[str],
    ) -> dict[str, Any]:
        teacher_names = {teacher.id: teacher.name for teacher in teachers}
        day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        month_names = [
            "Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
        ]
        days = [
            {
                "day_index": index,
                "day_name": day_names[index],
                "date": dates_iso[index],
                "formatted": (
                    f"{day_names[index]} {week_dates[index].day} "
                    f"{month_names[week_dates[index].month - 1]}"
                ),
            }
            for index in range(DAYS)
        ]
        grid = []
        for period in range(PERIODS):
            row = []
            for day_index, date_str in enumerate(dates_iso):
                match = next(
                    (
                        assignment
                        for assignment in report.assignments
                        if assignment.slot.date == date_str
                        and assignment.slot.period == period
                    ),
                    None,
                )
                row.append(
                    {
                        "date": date_str,
                        "day_index": day_index,
                        "period": period,
                        "assigned": [
                            teacher_names.get(teacher_id, teacher_id)
                            for teacher_id in match.assigned_teachers
                        ] if match else [],
                        "deficit": match.deficit if match else 2,
                    }
                )
            grid.append(row)

        return {
            "status": report.solver_status,
            "is_optimal": report.is_optimal,
            "total_deficits": report.total_deficits,
            "max_difference": report.max_difference_in_load,
            "week_label": (
                f"Semana del {week_dates[0].day} al {week_dates[-1].day} de "
                f"{month_names[week_dates[0].month - 1]} de {week_dates[0].year}"
            ),
            "days": days,
            "grid": grid,
            "ranking": [
                {
                    "id": teacher.id,
                    "name": teacher.name,
                    "department": teacher.department,
                    "count": report.guard_counts_by_teacher.get(teacher.id, 0),
                }
                for teacher in sorted(
                    teachers,
                    key=lambda teacher: report.guard_counts_by_teacher.get(
                        teacher.id, 0
                    ),
                    reverse=True,
                )
            ],
            "incidents": report.deficit_incidents,
        }
