import numpy as np
from ortools.sat.python import cp_model
from src.strategy.optimization.constraints import ConstraintProvider


class TestNoOverlap:
    def test_no_overlap_same_employee(self, make_task, make_employee, make_context):
        t1 = make_task(0, earliest=0, latest=7200, duration=1800)
        t2 = make_task(1, earliest=0, latest=7200, duration=1800)
        emp = make_employee(0)
        ctx = make_context([t1, t2], [emp])
        model = cp_model.CpModel()
        cp = ConstraintProvider(model, ctx)
        cp.define_variables(0, 7200)
        cp.add_constraints()
        model.Minimize(cp.get_objective_expr())
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        s0, e0 = solver.Value(cp.start[0]), solver.Value(cp.end[0])
        s1, e1 = solver.Value(cp.start[1]), solver.Value(cp.end[1])
        assert s1 >= e0 or s0 >= e1

    def test_travel_time_enforced(self, make_task, make_employee, make_context):
        dm = np.array([[0, 600], [600, 0]], dtype=float)
        t1 = make_task(0, location_idx=0, earliest=0, latest=7200, duration=1800)
        t2 = make_task(1, location_idx=1, earliest=0, latest=7200, duration=1800)
        emp = make_employee(0)
        ctx = make_context([t1, t2], [emp], dm)
        model = cp_model.CpModel()
        cp = ConstraintProvider(model, ctx)
        cp.define_variables(0, 7200)
        cp.add_constraints()
        model.Minimize(cp.get_objective_expr())
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        s0, e0 = solver.Value(cp.start[0]), solver.Value(cp.end[0])
        s1, e1 = solver.Value(cp.start[1]), solver.Value(cp.end[1])
        if s0 < s1:
            assert s1 >= e0 + 600
        else:
            assert s0 >= e1 + 600

    def test_certificate_filter(self, make_task, make_employee, make_context):
        t1 = make_task(0, required_certs=["CERT_A"])
        emp_no_cert = make_employee(0, certs=set())
        ctx = make_context([t1], [emp_no_cert])
        model = cp_model.CpModel()
        cp = ConstraintProvider(model, ctx)
        cp.define_variables(0, 7200)
        cp.add_constraints()
        model.Minimize(cp.get_objective_expr())
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        assert solver.Value(cp.is_dropped[0]) == 1

    def test_precedence_constraint(self, make_task, make_employee, make_context):
        t1 = make_task(0, earliest=0, latest=7200, duration=1800, aircraft_id="AC1")
        t2 = make_task(1, earliest=0, latest=7200, duration=1800, aircraft_id="AC1", deps=["T0"])
        emp = make_employee(0)
        ctx = make_context([t1, t2], [emp])
        model = cp_model.CpModel()
        cp = ConstraintProvider(model, ctx)
        cp.define_variables(0, 7200)
        cp.add_constraints()
        model.Minimize(cp.get_objective_expr())
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        if solver.Value(cp.is_dropped[0]) == 0 and solver.Value(cp.is_dropped[1]) == 0:
            assert solver.Value(cp.start[1]) >= solver.Value(cp.end[0])
