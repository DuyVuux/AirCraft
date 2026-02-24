from typing import List, Dict, Any, Tuple
from ortools.sat.python import cp_model
from src.strategy.optimization.models import OptimizationContext, OptimizationTask, OptimizationEmployee
import math

class ConstraintProvider:
    def __init__(self, model: cp_model.CpModel, context: OptimizationContext):
        self.model = model
        self.ctx = context

        self.x = {}
        self.start = {}
        self.end = {}
        self.is_dropped = {}

        self.task_intervals = {}
        self.emp_tasks = {e.id: [] for e in self.ctx.employees}

    def define_variables(self, horizon_min: int, horizon_max: int):
        for t in self.ctx.tasks:
            relevant_durs = [d for (tid, lvl), d in self.ctx.task_level_durations.items() if tid == t.id]
            if not relevant_durs:
                min_dur = t.duration
                max_dur = t.duration
            else:
                min_dur = min(relevant_durs)
                max_dur = max(relevant_durs)

            s_var = self.model.NewIntVar(t.earliest_start, t.latest_finish - min_dur, f'start_{t.id}')
            e_var = self.model.NewIntVar(t.earliest_start + min_dur, t.latest_finish, f'end_{t.id}')

            dur_var = self.model.NewIntVar(0, max_dur, f'duration_{t.id}')

            is_performed = self.model.NewBoolVar(f'performed_{t.id}')
            self.is_dropped[t.id] = self.model.NewBoolVar(f'dropped_{t.id}')
            self.model.Add(self.is_dropped[t.id] == is_performed.Not())

            interval = self.model.NewOptionalIntervalVar(
                s_var, dur_var, e_var, is_performed, f'interval_{t.id}'
            )

            self.start[t.id] = s_var
            self.end[t.id] = e_var
            self.task_intervals[t.id] = interval

            dur_terms = []

            for emp in self.ctx.employees:
                if self._can_perform(t, emp):
                    x_var = self.model.NewBoolVar(f'x_{t.id}_{emp.id}')
                    self.x[(t.id, emp.id)] = x_var

                    spec_dur = self.ctx.task_level_durations.get((t.id, emp.level), t.duration)
                    dur_terms.append(x_var * spec_dur)

                    emp_interval = self.model.NewOptionalIntervalVar(
                        s_var, spec_dur, e_var, x_var, f'interval_{t.id}_{emp.id}'
                    )
                    self.emp_tasks[emp.id].append({
                        'task': t,
                        'interval': emp_interval,
                        'start': s_var,
                        'end': e_var,
                        'active': x_var
                    })

            if dur_terms:
                self.model.Add(dur_var == sum(dur_terms))

    def add_constraints(self):
        for t in self.ctx.tasks:
            possible_emps = [self.x[(t.id, e.id)] for e in self.ctx.employees if (t.id, e.id) in self.x]
            self.model.Add(sum(possible_emps) + self.is_dropped[t.id] == 1)

        for emp_id, items in self.emp_tasks.items():
            if not items:
                continue

            intervals = [item['interval'] for item in items]

            emp = next((e for e in self.ctx.employees if e.id == emp_id), None)
            if emp and emp.breaks:
                for b_idx, (b_start, b_end) in enumerate(emp.breaks):
                    break_interval = self.model.NewFixedSizeIntervalVar(
                        b_start, b_end - b_start, f'break_e{emp_id}_{b_idx}_{b_start}'
                    )
                    intervals.append(break_interval)

            self.model.AddNoOverlap(intervals)

            self._add_pairwise_travel_constraints(emp_id, items)

        self._add_dependency_constraints()

    def _add_pairwise_travel_constraints(self, emp_id: int, items: list):
        if self.ctx.distance_matrix is None or len(items) < 2:
            return

        sorted_items = sorted(items, key=lambda it: it['task'].earliest_start)

        for i in range(len(sorted_items)):
            task_i = sorted_items[i]['task']
            start_i = sorted_items[i]['start']
            end_i = sorted_items[i]['end']
            active_i = sorted_items[i]['active']

            for j in range(i + 1, len(sorted_items)):
                task_j = sorted_items[j]['task']
                start_j = sorted_items[j]['start']
                end_j = sorted_items[j]['end']
                active_j = sorted_items[j]['active']

                if task_i.location_idx == task_j.location_idx:
                    continue

                loc_i = task_i.location_idx
                loc_j = task_j.location_idx

                travel_time_val = self.ctx.distance_matrix[loc_i, loc_j]

                if travel_time_val == 0 or math.isinf(travel_time_val):
                    continue

                travel_time = int(travel_time_val)

                if task_i.latest_finish + travel_time < task_j.earliest_start:
                    self.model.Add(
                        start_j >= end_i + travel_time
                    ).OnlyEnforceIf([active_i, active_j])
                elif task_j.latest_finish + travel_time < task_i.earliest_start:
                    self.model.Add(
                        start_i >= end_j + travel_time
                    ).OnlyEnforceIf([active_i, active_j])
                else:
                    order_var = self.model.NewBoolVar(
                        f'order_e{emp_id}_t{task_i.id}_t{task_j.id}'
                    )
                    self.model.Add(
                        start_j >= end_i + travel_time
                    ).OnlyEnforceIf([active_i, active_j, order_var])
                    self.model.Add(
                        start_i >= end_j + travel_time
                    ).OnlyEnforceIf([active_i, active_j, order_var.Not()])

    def _can_perform(self, task: OptimizationTask, emp: OptimizationEmployee) -> bool:
        for req in task.required_certs:
            if req not in emp.certs:
                return False
        if emp.level < task.min_level:
            return False
        return True

    def _add_dependency_constraints(self):
        task_by_aircraft_code = {}
        for t in self.ctx.tasks:
            key = (t.aircraft_id, t.original_task_code)
            task_by_aircraft_code[key] = t

        for t in self.ctx.tasks:
            for dep_code in t.dependencies:
                pred_key = (t.aircraft_id, dep_code)
                pred = task_by_aircraft_code.get(pred_key)
                if pred:
                    is_pred_dropped = self.is_dropped.get(pred.id)
                    is_curr_dropped = self.is_dropped.get(t.id)

                    if is_pred_dropped is not None and is_curr_dropped is not None:
                        both_performed = self.model.NewBoolVar(f'both_perf_{pred.id}_{t.id}')
                        self.model.AddBoolAnd([is_pred_dropped.Not(), is_curr_dropped.Not()]).OnlyEnforceIf(both_performed)
                        self.model.AddBoolOr([is_pred_dropped, is_curr_dropped]).OnlyEnforceIf(both_performed.Not())

                        self.model.Add(self.start[t.id] >= self.end[pred.id]).OnlyEnforceIf(both_performed)

    def get_objective_expr(self, w_drop=100_000_000, w_employee=10_000):
        total_dropped = sum(self.is_dropped[t.id] for t in self.ctx.tasks)

        emp_active_vars = []
        for emp in self.ctx.employees:
            emp_tasks = [
                self.x[(t.id, emp.id)]
                for t in self.ctx.tasks
                if (t.id, emp.id) in self.x
            ]
            if emp_tasks:
                emp_has_task = self.model.NewBoolVar(f'emp_active_{emp.id}')
                self.model.AddMaxEquality(emp_has_task, emp_tasks)
                emp_active_vars.append(emp_has_task)

        active_employees = sum(emp_active_vars) if emp_active_vars else 0

        return total_dropped * w_drop + active_employees * w_employee
