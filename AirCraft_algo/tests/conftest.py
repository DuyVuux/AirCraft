import pytest
import numpy as np
from ortools.sat.python import cp_model
from src.strategy.optimization.models import (
    OptimizationContext,
    OptimizationTask,
    OptimizationEmployee,
)


@pytest.fixture
def make_task():
    def _make(task_id, location_idx=0, earliest=0, latest=7200, duration=1800,
              aircraft_id="AC1", required_certs=None, min_level=1, deps=None):
        return OptimizationTask(
            id=task_id,
            original_task_code=f"T{task_id}",
            aircraft_id=aircraft_id,
            earliest_start=earliest,
            latest_finish=latest,
            duration=duration,
            location_idx=location_idx,
            required_certs=required_certs or [],
            min_level=min_level,
            dependencies=deps or [],
        )
    return _make


@pytest.fixture
def make_employee():
    def _make(emp_id, certs=None, level=1, shifts=None, breaks=None):
        return OptimizationEmployee(
            id=emp_id,
            original_id=f"EMP{emp_id}",
            certs=certs or set(),
            level=level,
            shifts=shifts or [(0, 86400)],
            breaks=breaks or [],
        )
    return _make


@pytest.fixture
def make_context():
    def _make(tasks, employees, distance_matrix=None, task_level_durations=None):
        if distance_matrix is None:
            max_loc = max(t.location_idx for t in tasks) + 1 if tasks else 1
            distance_matrix = np.zeros((max_loc, max_loc), dtype=float)
        return OptimizationContext(
            tasks=tasks,
            employees=employees,
            cert_to_idx={},
            idx_to_cert={},
            location_to_idx={},
            distance_matrix=distance_matrix,
            task_map={t.id: (t.aircraft_id, t.original_task_code) for t in tasks},
            task_level_durations=task_level_durations or {},
        )
    return _make
