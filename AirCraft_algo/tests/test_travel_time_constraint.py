import numpy as np
import pytest
from ortools.sat.python import cp_model
from src.strategy.optimization.models import (
    OptimizationContext,
    OptimizationTask,
    OptimizationEmployee,
    SolutionState,
)
from src.strategy.optimization.constraints import ConstraintProvider


def _make_context(tasks, employees, distance_matrix, task_level_durations=None):
    return OptimizationContext(
        tasks=tasks,
        employees=employees,
        cert_to_idx={},
        idx_to_cert={},
        location_to_idx={"LOC_A": 0, "LOC_B": 1},
        distance_matrix=distance_matrix,
        task_map={t.id: (t.aircraft_id, t.original_task_code) for t in tasks},
        task_level_durations=task_level_durations or {},
    )


def _make_task(task_id, location_idx, earliest, latest, duration, aircraft_id="AC1"):
    return OptimizationTask(
        id=task_id,
        original_task_code=f"T{task_id}",
        aircraft_id=aircraft_id,
        earliest_start=earliest,
        latest_finish=latest,
        duration=duration,
        location_idx=location_idx,
        required_certs=[],
        min_level=1,
    )


def _make_employee(emp_id, certs=None, level=1, shifts=None, breaks=None):
    return OptimizationEmployee(
        id=emp_id,
        original_id=f"EMP{emp_id}",
        certs=certs or set(),
        level=level,
        shifts=shifts or [(0, 86400)],
        breaks=breaks or [],
    )


class TestPairwiseTravelTime:
    def test_two_tasks_different_locations_enforces_travel_gap(self):
        travel_time = 600
        dm = np.array([[0, travel_time], [travel_time, 0]], dtype=float)

        task_a = _make_task(0, location_idx=0, earliest=0, latest=7200, duration=1800)
        task_b = _make_task(1, location_idx=1, earliest=0, latest=7200, duration=1800)
        emp = _make_employee(0)

        ctx = _make_context([task_a, task_b], [emp], dm)

        model = cp_model.CpModel()
        cp = ConstraintProvider(model, ctx)
        cp.define_variables(0, 7200)
        cp.add_constraints()
        model.Minimize(cp.get_objective_expr())

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

        s0 = solver.Value(cp.start[0])
        e0 = solver.Value(cp.end[0])
        s1 = solver.Value(cp.start[1])
        e1 = solver.Value(cp.end[1])

        if s0 < s1:
            assert s1 >= e0 + travel_time, f"Task 1 start {s1} < Task 0 end {e0} + travel {travel_time}"
        else:
            assert s0 >= e1 + travel_time, f"Task 0 start {s0} < Task 1 end {e1} + travel {travel_time}"

    def test_same_location_no_travel_constraint(self):
        dm = np.array([[0, 600], [600, 0]], dtype=float)

        task_a = _make_task(0, location_idx=0, earliest=0, latest=7200, duration=1800)
        task_b = _make_task(1, location_idx=0, earliest=0, latest=7200, duration=1800)
        emp = _make_employee(0)

        ctx = _make_context([task_a, task_b], [emp], dm)

        model = cp_model.CpModel()
        cp = ConstraintProvider(model, ctx)
        cp.define_variables(0, 7200)
        cp.add_constraints()
        model.Minimize(cp.get_objective_expr())

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

        s0 = solver.Value(cp.start[0])
        e0 = solver.Value(cp.end[0])
        s1 = solver.Value(cp.start[1])
        e1 = solver.Value(cp.end[1])

        gap = abs(min(s0, s1) - max(e0, e1)) if s0 < s1 else abs(min(s1, s0) - max(e1, e0))
        if s0 < s1:
            assert s1 >= e0
        else:
            assert s0 >= e1

    def test_inf_travel_time_skipped(self):
        dm = np.array([[0, float('inf')], [float('inf'), 0]], dtype=float)

        task_a = _make_task(0, location_idx=0, earliest=0, latest=7200, duration=1800)
        task_b = _make_task(1, location_idx=1, earliest=0, latest=7200, duration=1800)
        emp = _make_employee(0)

        ctx = _make_context([task_a, task_b], [emp], dm)

        model = cp_model.CpModel()
        cp = ConstraintProvider(model, ctx)
        cp.define_variables(0, 7200)
        cp.add_constraints()
        model.Minimize(cp.get_objective_expr())

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    def test_zero_travel_time_skipped(self):
        dm = np.array([[0, 0], [0, 0]], dtype=float)

        task_a = _make_task(0, location_idx=0, earliest=0, latest=7200, duration=1800)
        task_b = _make_task(1, location_idx=1, earliest=0, latest=7200, duration=1800)
        emp = _make_employee(0)

        ctx = _make_context([task_a, task_b], [emp], dm)

        model = cp_model.CpModel()
        cp = ConstraintProvider(model, ctx)
        cp.define_variables(0, 7200)
        cp.add_constraints()
        model.Minimize(cp.get_objective_expr())

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)


class TestObjectiveFunction:
    def test_objective_minimizes_dropped_and_employees(self):
        dm = np.array([[0, 0], [0, 0]], dtype=float)

        task_a = _make_task(0, location_idx=0, earliest=0, latest=7200, duration=1800)
        emp = _make_employee(0)

        ctx = _make_context([task_a], [emp], dm)

        model = cp_model.CpModel()
        cp = ConstraintProvider(model, ctx)
        cp.define_variables(0, 7200)
        cp.add_constraints()
        obj = cp.get_objective_expr()
        model.Minimize(obj)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        assert solver.Value(cp.is_dropped[0]) == 0

    def test_active_employee_penalty_prefers_fewer_employees(self):
        dm = np.array([[0]], dtype=float)

        task_a = _make_task(0, location_idx=0, earliest=0, latest=7200, duration=1800)
        task_b = _make_task(1, location_idx=0, earliest=0, latest=7200, duration=1800)
        emp_a = _make_employee(0)
        emp_b = _make_employee(1)

        ctx = _make_context([task_a, task_b], [emp_a, emp_b], dm)

        model = cp_model.CpModel()
        cp = ConstraintProvider(model, ctx)
        cp.define_variables(0, 7200)
        cp.add_constraints()
        model.Minimize(cp.get_objective_expr())

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

        emp0_assigned = any(
            solver.Value(cp.x[(t.id, 0)]) for t in ctx.tasks if (t.id, 0) in cp.x
        )
        emp1_assigned = any(
            solver.Value(cp.x[(t.id, 1)]) for t in ctx.tasks if (t.id, 1) in cp.x
        )
        active_count = int(emp0_assigned) + int(emp1_assigned)
        assert active_count == 1


class TestBreakNameCollision:
    def test_multiple_breaks_no_name_collision(self):
        dm = np.array([[0]], dtype=float)

        task_a = _make_task(0, location_idx=0, earliest=0, latest=14400, duration=1800)
        emp = _make_employee(0, breaks=[(3600, 4200), (7200, 7800), (10800, 11400)])

        ctx = _make_context([task_a], [emp], dm)

        model = cp_model.CpModel()
        cp = ConstraintProvider(model, ctx)
        cp.define_variables(0, 14400)
        cp.add_constraints()
        model.Minimize(cp.get_objective_expr())

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
