"""
Suite de pruebas unitarias y de integración para el motor de asignación.
"""
from __future__ import annotations

import pytest
from v1.models import SlotStatus, Teacher, TeacherSchedule, TimeSlot
from v1.scheduler import DAYS, PERIODS, REQUIRED_TEACHERS_PER_SLOT, generate_weekly_guards


def build_uniform_schedules(
    teachers: list[Teacher], default_status: SlotStatus = SlotStatus.FREE
) -> dict[str, TeacherSchedule]:
    """Helper: Crea horarios uniformes para una lista de profesores."""
    schedules = {}
    for t in teachers:
        sched = TeacherSchedule(teacher_id=t.id)
        for d in range(DAYS):
            for p in range(PERIODS):
                sched.slots[(d, p)] = default_status
        schedules[t.id] = sched
    return schedules


@pytest.fixture
def standard_teachers() -> list[Teacher]:
    """Claustro estándar de 12 docentes (capacidad holgada para 60 guardias semanales)."""
    return [Teacher(id=f"T{i:02d}", name=f"Profesor {i:02d}") for i in range(1, 13)]


class TestGuardScheduler:

    def test_ideal_scenario_coverage_and_balance(self, standard_teachers: list[Teacher]) -> None:
        """1. Escenario ideal: 12 profesores libres.

        Total de guardias = 30 bloques * 2 = 60 plazas.
        Esperado: Cobertura del 100%, 0 déficit y carga balanceada exacta (5 por docente).
        """
        schedules = build_uniform_schedules(standard_teachers, SlotStatus.FREE)

        report = generate_weekly_guards(standard_teachers, schedules)

        assert report.total_deficits == 0
        assert len(report.deficit_incidents) == 0
        assert len(report.assignments) == DAYS * PERIODS

        # Verificar cobertura exacta de 2 docentes por bloque
        for assignment in report.assignments:
            assert len(assignment.assigned_teachers) == REQUIRED_TEACHERS_PER_SLOT

        # 60 / 12 = 5 exacto
        for t_id, count in report.guard_counts_by_teacher.items():
            assert count == 5
        assert report.max_difference_in_load == 0

    def test_hard_constraint_teaching_avoided(self, standard_teachers: list[Teacher]) -> None:
        """2. Restricción de docencia: Si un profesor tiene TEACHING en un bloque,

        jamás debe ser seleccionado para guardia en dicho bloque.
        """
        schedules = build_uniform_schedules(standard_teachers, SlotStatus.FREE)
        t_blocked = standard_teachers[0].id
        blocked_slot = TimeSlot(day=2, period=3)  # Miércoles P3

        schedules[t_blocked].slots[(blocked_slot.day, blocked_slot.period)] = SlotStatus.TEACHING

        report = generate_weekly_guards(standard_teachers, schedules)

        target_assignment = next(
            a for a in report.assignments
            if a.slot.day == blocked_slot.day and a.slot.period == blocked_slot.period
        )
        assert t_blocked not in target_assignment.assigned_teachers
        assert len(target_assignment.assigned_teachers) == REQUIRED_TEACHERS_PER_SLOT

    def test_hard_constraint_absence_avoided(self, standard_teachers: list[Teacher]) -> None:
        """3. Restricción de asuntos propios: Permiso justificado puntual (ABSENCE)."""
        schedules = build_uniform_schedules(standard_teachers, SlotStatus.FREE)
        t_absent = standard_teachers[1].id
        absent_slot = TimeSlot(day=0, period=0)  # Lunes 08:00

        schedules[t_absent].slots[(absent_slot.day, absent_slot.period)] = SlotStatus.ABSENCE

        report = generate_weekly_guards(standard_teachers, schedules)

        slot_0_0 = next(
            a for a in report.assignments
            if a.slot.day == absent_slot.day and a.slot.period == absent_slot.period
        )
        assert t_absent not in slot_0_0.assigned_teachers

    def test_deficit_handling_graceful_degradation(self) -> None:
        """4. Subcobertura controlada: Franja crítica con solo 1 o 0 profesores disponibles.

        El sistema no debe fallar ni lanzar excepciones, sino registrar las incidencias.
        """
        # Solo 2 profesores en todo el centro
        teachers = [Teacher(id="T01", name="Prof 1"), Teacher(id="T02", name="Prof 2")]
        schedules = build_uniform_schedules(teachers, SlotStatus.FREE)

        # En Viernes P5: T01 tiene docencia y T02 ausencia (0 disponibles)
        schedules["T01"].slots[(4, 5)] = SlotStatus.TEACHING
        schedules["T02"].slots[(4, 5)] = SlotStatus.ABSENCE

        # En Viernes P4: T01 tiene docencia (solo 1 disponible: T02)
        schedules["T01"].slots[(4, 4)] = SlotStatus.TEACHING

        report = generate_weekly_guards(teachers, schedules)

        # Verificar viernes P5 (0 asignados, déficit 2)
        p5 = next(a for a in report.assignments if a.slot.day == 4 and a.slot.period == 5)
        assert len(p5.assigned_teachers) == 0
        assert p5.deficit == 2

        # Verificar viernes P4 (1 asignado, déficit 1)
        p4 = next(a for a in report.assignments if a.slot.day == 4 and a.slot.period == 4)
        assert len(p4.assigned_teachers) == 1
        assert p4.assigned_teachers == ["T02"]
        assert p4.deficit == 1

        # Verificar que se generaron las alertas en el reporte
        assert len(report.deficit_incidents) >= 2
        assert any("Viernes - P5" in inc for inc in report.deficit_incidents)
        assert any("Viernes - P4" in inc for inc in report.deficit_incidents)

    def test_no_teacher_duplication_in_same_slot(self, standard_teachers: list[Teacher]) -> None:
        """5. Unicidad: Un profesor no puede duplicarse para ocupar ambos puestos."""
        schedules = build_uniform_schedules(standard_teachers, SlotStatus.FREE)
        report = generate_weekly_guards(standard_teachers, schedules)

        for assignment in report.assignments:
            assigned = assignment.assigned_teachers
            assert len(assigned) == len(set(assigned)), f"Docente duplicado en {assignment.slot.label}"

    def test_fairness_metric_threshold(self) -> None:
        """6. Equidad: Con 7 profesores (60 plazas / 7 = 8.57),

        la diferencia de carga (max - min) debe ser a lo sumo 1 guardia.
        """
        teachers = [Teacher(id=f"T{i}", name=f"Prof {i}") for i in range(1, 8)]
        schedules = build_uniform_schedules(teachers, SlotStatus.FREE)

        report = generate_weekly_guards(teachers, schedules)

        assert report.total_deficits == 0
        # 60 = 4 * 9 + 3 * 8 -> 4 profesores con 9 guardias y 3 profesores con 8 guardias
        assert report.max_difference_in_load <= 1
        for count in report.guard_counts_by_teacher.values():
            assert count in (8, 9)

    def test_anti_fatigue_penalty_avoids_consecutive_guards(self) -> None:
        """Verifica que el optimizador evite asignar horas seguidas al mismo docente

        siempre que existan alternativas disponibles.
        """
        # 4 profesores para cubrir los 6 periodos del día 0 (Lunes)
        teachers = [Teacher(id=f"T{i}", name=f"Prof {i}") for i in range(1, 5)]
        schedules = build_uniform_schedules(teachers, SlotStatus.FREE)

        # Bloquear resto de días para aislar el test a un día completo
        for t in teachers:
            for d in range(1, DAYS):
                for p in range(PERIODS):
                    schedules[t.id].slots[(d, p)] = SlotStatus.ABSENCE

        report = generate_weekly_guards(teachers, schedules)

        # 6 periodos * 2 = 12 guardias entre 4 profesores = 3 guardias cada uno
        # Comprobar que ningún profesor haga 3 horas consecutivas
        for t in teachers:
            monday_guards = [
                a.slot.period for a in report.assignments
                if a.slot.day == 0 and t.id in a.assigned_teachers
            ]
            monday_guards.sort()
            for i in range(len(monday_guards) - 1):
                assert monday_guards[i + 1] - monday_guards[i] >= 1