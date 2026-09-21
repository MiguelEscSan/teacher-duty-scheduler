from __future__ import annotations

from ortools.sat.python import cp_model

from src.domain.constants import PERIODS, REQUIRED_TEACHERS_PER_SLOT
from src.domain.guard import AssignmentReport, GuardAssignment
from src.domain.ports.guard_optimizer import GuardOptimizer
from src.domain.schedule import TeacherSchedule, TimeSlot
from src.domain.teacher import Teacher


class ORToolsGuardOptimizer(GuardOptimizer):
    def generate_schedule(
        self,
        teachers: list[Teacher],
        slots: list[TimeSlot],
        schedules: dict[str, TeacherSchedule],
        time_limit_seconds: float = 6.0,
    ) -> AssignmentReport:
        model = cp_model.CpModel()
        teacher_ids = [teacher.id for teacher in teachers]

        if not teacher_ids or not slots:
            return AssignmentReport([], {}, ["Sin docentes o franjas"], "NO_DATA", False)

        x: dict[tuple[str, str, int], cp_model.IntVar] = {}
        for teacher_id in teacher_ids:
            schedule = schedules.get(teacher_id, TeacherSchedule(teacher_id=teacher_id))
            for slot in slots:
                if schedule.is_available(slot):
                    x[teacher_id, slot.date, slot.period] = model.NewBoolVar(
                        f"x_{teacher_id}_{slot.date}_{slot.period}"
                    )
                else:
                    x[teacher_id, slot.date, slot.period] = model.NewConstant(0)

        deficit_vars: dict[tuple[str, int], cp_model.IntVar] = {}
        for slot in slots:
            deficit_vars[slot.date, slot.period] = model.NewIntVar(
                0,
                REQUIRED_TEACHERS_PER_SLOT,
                f"def_{slot.date}_{slot.period}",
            )
            assigned_in_slot = [
                x[teacher_id, slot.date, slot.period] for teacher_id in teacher_ids
            ]
            model.Add(
                sum(assigned_in_slot) + deficit_vars[slot.date, slot.period]
                == REQUIRED_TEACHERS_PER_SLOT
            )

        teacher_totals: dict[str, cp_model.IntVar] = {}
        for teacher_id in teacher_ids:
            total = model.NewIntVar(0, len(slots), f"tot_{teacher_id}")
            model.Add(
                total
                == sum(x[teacher_id, slot.date, slot.period] for slot in slots)
            )
            teacher_totals[teacher_id] = total

        max_load = model.NewIntVar(0, len(slots), "max_load")
        min_load = model.NewIntVar(0, len(slots), "min_load")
        model.AddMaxEquality(max_load, list(teacher_totals.values()))
        model.AddMinEquality(min_load, list(teacher_totals.values()))

        load_diff = model.NewIntVar(0, len(slots), "load_diff")
        model.Add(load_diff == max_load - min_load)

        dates = sorted({slot.date for slot in slots})
        consecutive_penalties: list[cp_model.IntVar] = []
        for teacher_id in teacher_ids:
            for date_str in dates:
                for period in range(PERIODS - 1):
                    current = (teacher_id, date_str, period)
                    following = (teacher_id, date_str, period + 1)
                    if current in x and following in x:
                        consecutive = model.NewBoolVar(
                            f"c_{teacher_id}_{date_str}_{period}"
                        )
                        model.AddBoolAnd([x[current], x[following]]).OnlyEnforceIf(consecutive)
                        model.AddBoolOr(
                            [x[current].Not(), x[following].Not()]
                        ).OnlyEnforceIf(consecutive.Not())
                        consecutive_penalties.append(consecutive)

        model.Minimize(
            10_000 * sum(deficit_vars.values())
            + 100 * load_diff
            + 10 * sum(consecutive_penalties)
        )

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_seconds
        status = solver.Solve(model)

        assignments: list[GuardAssignment] = []
        incidents: list[str] = []
        counts = {teacher_id: 0 for teacher_id in teacher_ids}

        for slot in slots:
            assigned = [
                teacher_id
                for teacher_id in teacher_ids
                if solver.Value(x[teacher_id, slot.date, slot.period]) == 1
            ]
            for teacher_id in assigned:
                counts[teacher_id] += 1

            assignment = GuardAssignment(slot=slot, assigned_teachers=assigned)
            assignments.append(assignment)
            if assignment.deficit > 0:
                incidents.append(f"{slot.label}: Faltan {assignment.deficit} profesor(es)")

        return AssignmentReport(
            assignments=assignments,
            guard_counts_by_teacher=counts,
            deficit_incidents=incidents,
            solver_status=solver.StatusName(status),
            is_optimal=status == cp_model.OPTIMAL,
        )
