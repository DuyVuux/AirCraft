import math
import numpy as np
from src.strategy.optimization.solver import LNSSolver
from src.strategy.optimization.models import SolutionState, OptimizationTask, OptimizationEmployee, OptimizationContext


def _minimal_context(n_tasks=3):
    tasks = [
        OptimizationTask(
            id=i, original_task_code=f"T{i}", aircraft_id="AC1",
            earliest_start=0, latest_finish=14400, duration=1800,
            location_idx=0, required_certs=[], min_level=1,
        ) for i in range(n_tasks)
    ]
    emp = OptimizationEmployee(
        id=0, original_id="E0", certs=set(), level=1,
        shifts=[(0, 86400)], breaks=[],
    )
    return OptimizationContext(
        tasks=tasks, employees=[emp],
        cert_to_idx={}, idx_to_cert={},
        location_to_idx={}, distance_matrix=np.zeros((1, 1)),
        task_map={t.id: (t.aircraft_id, t.original_task_code) for t in tasks},
        task_level_durations={},
    )


class TestLNSSolver:
    def test_sa_accepts_better(self):
        solver = LNSSolver(time_limit_seconds=5)
        solver.ctx = _minimal_context()
        better = SolutionState()
        better.assignments = {0: 0}
        better.start_times = {0: 0}
        worse = SolutionState()
        worse.assignments = {0: 0}
        worse.start_times = {0: 0}
        worse.dropped_tasks = [1]
        assert solver._accept_worse(worse, better, 100.0) is True

    def test_sa_rejects_at_zero_temp(self):
        solver = LNSSolver(time_limit_seconds=5)
        solver.ctx = _minimal_context()
        current = SolutionState()
        current.assignments = {0: 0}
        current.start_times = {0: 0}
        candidate = SolutionState()
        candidate.assignments = {0: 0}
        candidate.start_times = {0: 0}
        candidate.dropped_tasks = [1]
        assert solver._accept_worse(current, candidate, 0.0) is False

    def test_cost_includes_travel(self):
        solver = LNSSolver(time_limit_seconds=5)
        ctx = _minimal_context(2)
        ctx.tasks[0].location_idx = 0
        ctx.tasks[1].location_idx = 1
        ctx.distance_matrix = np.array([[0, 300], [300, 0]], dtype=float)
        solver.ctx = ctx
        sol = SolutionState()
        sol.assignments = {0: 0, 1: 0}
        sol.start_times = {0: 0, 1: 2100}
        cost = solver._calculate_cost(sol)
        assert cost > 10000

    def test_cost_dropped_penalty(self):
        solver = LNSSolver(time_limit_seconds=5)
        solver.ctx = _minimal_context(1)
        sol = SolutionState()
        sol.dropped_tasks = [0]
        cost = solver._calculate_cost(sol)
        assert cost >= 1_000_000
