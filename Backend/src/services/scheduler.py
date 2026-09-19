"""
Optimizador de guardias basado en OR-Tools CP-SAT con soporte de fechas concretas.
"""
from __future__ import annotations
from ortools.sat.python import cp_model
from src.domain.entities import AssignmentReport, GuardAssignment, Teacher, TeacherSchedule, TimeSlot
from src.domain.constants import REQUIRED_TEACHERS_PER_SLOT, PERIODS


def generate_guards_for_slots(
    teachers: list[Teacher],
    slots: list[TimeSlot],
    schedules: dict[str, TeacherSchedule],
    time_limit_seconds: float = 6.0,
) -> AssignmentReport:
    model = cp_model.CpModel()
    teacher_ids = [t.id for t in teachers]

    if not teacher_ids or not slots:
        return AssignmentReport([], {}, ["Sin docentes o franjas"], "NO_DATA", False)

    # 1. Variables de decisión x[t, date, period]
    x: dict[tuple[str, str, int], cp_model.IntVar] = {}
    for t_id in teacher_ids:
        sched = schedules.get(t_id, TeacherSchedule(teacher_id=t_id))
        for slot in slots:
            if sched.is_available(slot):
                x[t_id, slot.date, slot.period] = model.NewBoolVar(f"x_{t_id}_{slot.date}_{slot.period}")
            else:
                x[t_id, slot.date, slot.period] = model.NewConstant(0)

    # 2. Cobertura obligatoria por bloque con variables de holgura (Déficit)
    deficit_vars: dict[tuple[str, int], cp_model.IntVar] = {}
    for slot in slots:
        deficit_vars[slot.date, slot.period] = model.NewIntVar(
            0, REQUIRED_TEACHERS_PER_SLOT, f"def_{slot.date}_{slot.period}"
        )
        assigned_in_slot = [x[t_id, slot.date, slot.period] for t_id in teacher_ids]
        model.Add(sum(assigned_in_slot) + deficit_vars[slot.date, slot.period] == REQUIRED_TEACHERS_PER_SLOT)

    # 3. Equidad en la carga total del periodo analizado
    teacher_totals: dict[str, cp_model.IntVar] = {}
    for t_id in teacher_ids:
        t_var = model.NewIntVar(0, len(slots), f"tot_{t_id}")
        model.Add(t_var == sum(x[t_id, s.date, s.period] for s in slots))
        teacher_totals[t_id] = t_var

    max_load = model.NewIntVar(0, len(slots), "max_load")
    min_load = model.NewIntVar(0, len(slots), "min_load")
    model.AddMaxEquality(max_load, list(teacher_totals.values()))
    model.AddMinEquality(min_load, list(teacher_totals.values()))

    load_diff = model.NewIntVar(0, len(slots), "load_diff")
    model.Add(load_diff == max_load - min_load)

    # 4. Anti-fatiga consecutiva diaria
    dates = sorted(list({s.date for s in slots}))
    consecutive_penalties: list[cp_model.IntVar] = []
    for t_id in teacher_ids:
        for d_str in dates:
            for p in range(PERIODS - 1):
                # Si existen ambas franjas consecutivas
                if (t_id, d_str, p) in x and (t_id, d_str, p + 1) in x:
                    c_var = model.NewBoolVar(f"c_{t_id}_{d_str}_{p}")
                    model.AddBoolAnd([x[t_id, d_str, p], x[t_id, d_str, p + 1]]).OnlyEnforceIf(c_var)
                    model.AddBoolOr([x[t_id, d_str, p].Not(), x[t_id, d_str, p + 1].Not()]).OnlyEnforceIf(c_var.Not())
                    consecutive_penalties.append(c_var)

    # Función objetivo multiobjetivo
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
    counts = {t_id: 0 for t_id in teacher_ids}

    for slot in slots:
        assigned = [
            t_id for t_id in teacher_ids
            if solver.Value(x[t_id, slot.date, slot.period]) == 1
        ]
        for t_id in assigned:
            counts[t_id] += 1

        ga = GuardAssignment(slot=slot, assigned_teachers=assigned)
        assignments.append(ga)
        if ga.deficit > 0:
            incidents.append(f"{slot.label}: Faltan {ga.deficit} profesor(es)")

    return AssignmentReport(
        assignments=assignments,
        guard_counts_by_teacher=counts,
        deficit_incidents=incidents,
        solver_status=solver.StatusName(status),
        is_optimal=(status == cp_model.OPTIMAL),
    )