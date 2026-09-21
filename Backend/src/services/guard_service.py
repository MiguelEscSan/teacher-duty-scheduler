"""
Caso de uso orquestador para resolución de cuadrantes anclados a fechas reales.
"""
from datetime import datetime, timedelta
from src.domain.constants import DAYS, PERIODS
from src.domain import SlotStatus, Teacher, TeacherSchedule, TimeSlot
from src.infrastructure.repositories import SQLGuardRepository
from src.services.scheduler import generate_guards_for_slots


class GuardService:
    def __init__(self, repository: SQLGuardRepository):
        self.repository = repository

    def calculate_week(self, start_date_str: str) -> dict:
        # 1. Normalizar fecha al lunes de esa semana
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        if start_dt.weekday() != 0:
            start_dt = start_dt - timedelta(days=start_dt.weekday())

        # 2. Construir los 5 días lectivos y TimeSlots de la semana
        week_dates = [start_dt + timedelta(days=i) for i in range(DAYS)]
        dates_iso = [d.strftime("%Y-%m-%d") for d in week_dates]

        all_slots: list[TimeSlot] = []
        for day_idx, d_str in enumerate(dates_iso):
            for p in range(PERIODS):
                all_slots.append(TimeSlot(date=d_str, day_index=day_idx, period=p))

        # 3. Extraer entidades y base de datos
        teachers = self.repository.get_all_teachers()
        if not teachers:
            return {"error": "No hay profesores registrados."}

        base_schedules = self.repository.get_all_base_schedules()
        base_map = {
            (b.teacher_id, b.day_of_week, b.period):
            ("TEACHING" if b.is_teaching else "FREE")
            for b in base_schedules
        }

        # 4. Extraer ausencias que coincidan estrictamente con esas fechas
        absences = self.repository.get_absences_by_dates(dates_iso)
        absence_map = {(a.teacher_id, a.date, a.period): True for a in absences}

        # 5. Ensamblar TeacherSchedule proyectando horario base + ausencias
        schedules_map: dict[str, TeacherSchedule] = {}
        for t in teachers:
            sched = TeacherSchedule(teacher_id=t.id)
            for slot in all_slots:
                if (t.id, slot.date, slot.period) in absence_map:
                    sched.slots[(slot.date, slot.period)] = SlotStatus.ABSENCE
                else:
                    base_status = base_map.get((t.id, slot.day_index, slot.period), "FREE")
                    sched.slots[(slot.date, slot.period)] = SlotStatus(base_status)
            schedules_map[t.id] = sched

        # 6. Ejecutar Solver
        report = generate_guards_for_slots(teachers, all_slots, schedules_map)

        # 7. Formatear respuesta enriquecida con metadatos de fechas
        t_names = {t.id: t.name for t in teachers}
        day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        month_names = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

        days_metadata = [
            {
                "day_index": i,
                "day_name": day_names[i],
                "date": dates_iso[i],
                "formatted": f"{day_names[i]} {week_dates[i].day} {month_names[week_dates[i].month - 1]}"
            }
            for i in range(DAYS)
        ]

        grid_data = []
        for p in range(PERIODS):
            row = []
            for day_idx, d_str in enumerate(dates_iso):
                match = next((x for x in report.assignments if x.slot.date == d_str and x.slot.period == p), None)
                row.append({
                    "date": d_str,
                    "day_index": day_idx,
                    "period": p,
                    "assigned": [t_names.get(tid, tid) for tid in match.assigned_teachers] if match else [],
                    "deficit": match.deficit if match else 2
                })
            grid_data.append(row)

        return {
            "status": report.solver_status,
            "is_optimal": report.is_optimal,
            "total_deficits": report.total_deficits,
            "max_difference": report.max_difference_in_load,
            "week_label": f"Semana del {week_dates[0].day} al {week_dates[-1].day} de {month_names[week_dates[0].month - 1]} de {week_dates[0].year}",
            "days": days_metadata,
            "grid": grid_data,
            "ranking": [
                {"id": t.id, "name": t.name, "department": t.department ,"count": report.guard_counts_by_teacher.get(t.id, 0)}
                for t in sorted(teachers, key=lambda x: report.guard_counts_by_teacher.get(x.id, 0), reverse=True)
            ],
            "incidents": report.deficit_incidents
        }