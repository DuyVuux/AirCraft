"""
Employee Constraints - No-overlap, working time, breaks, and overtime.
"""
from typing import Dict, Any, List, Tuple
from src.strategy.orStrategy.constraints.base import ConstraintBuilder


class EmployeeConstraint(ConstraintBuilder):
    """
    Build employee constraints.
    
    Constraints:
    1. No-overlap: Tasks assigned to same employee cannot overlap
    2. Working time start: task.start >= employee.work_start - HARD
    3. Working time end: overtime penalty - SOFT
    4. Breaks: Break intervals added to no-overlap
    """
    
    def build(self, data: Dict[str, Any], variables: Dict[str, Any]) -> None:
        """Build all employee constraints."""
        self._build_no_overlap(data, variables)
        self._build_work_start_constraint(data, variables)
        self._build_overtime_slack(data, variables)
    
    def _build_no_overlap(self, data: Dict[str, Any], variables: Dict[str, Any]):
        """
        No-overlap constraint for each employee.
        
        Tasks assigned to same employee + break intervals cannot overlap.
        """
        employees = data['employees']
        task_vars = variables['tasks']
        
        for emp in employees:
            emp_intervals = []
            
            # Collect task intervals for this employee
            for t_idx, task_var in enumerate(task_vars):
                if emp.idx in task_var['assigned_vars']:
                    assign_var, _, _ = task_var['assigned_vars'][emp.idx]
                    
                    opt_interval = self.model.NewOptionalIntervalVar(
                        task_var['start'],
                        task_var['size'],
                        task_var['end'],
                        assign_var,
                        f'opt_int_e{emp.idx}_t{t_idx}'
                    )
                    emp_intervals.append(opt_interval)
            
            # Add break intervals
            for break_idx, (b_start, b_end) in enumerate(emp.breaks):
                break_interval = self.model.NewIntervalVar(
                    self.model.NewConstant(b_start),
                    self.model.NewConstant(b_end - b_start),
                    self.model.NewConstant(b_end),
                    f'break_e{emp.idx}_b{break_idx}'
                )
                emp_intervals.append(break_interval)
            
            # Add no-overlap constraint
            if emp_intervals:
                self.model.AddNoOverlap(emp_intervals)
    
    def _build_work_start_constraint(self, data: Dict[str, Any], variables: Dict[str, Any]):
        """
        HARD: Task must start after employee work start.
        
        Constraint: start >= work_start (when assigned to this employee)
        """
        employees = data['employees']
        task_vars = variables['tasks']
        
        for emp in employees:
            for task_var in task_vars:
                if emp.idx in task_var['assigned_vars']:
                    assign_var, _, _ = task_var['assigned_vars'][emp.idx]
                    
                    self.model.Add(
                        task_var['start'] >= emp.work_start
                    ).OnlyEnforceIf(assign_var)
    
    def _build_overtime_slack(self, data: Dict[str, Any], variables: Dict[str, Any]):
        """
        SOFT: Create slack variable for overtime penalty.
        
        overtime = max(0, end - work_end) when assigned
        Stored in variables['overtime_vars'] for ObjectiveBuilder.
        """
        employees = data['employees']
        task_vars = variables['tasks']
        max_time = data['max_time']
        
        overtime_vars: List[Tuple] = []
        
        for emp in employees:
            for t_idx, task_var in enumerate(task_vars):
                if emp.idx in task_var['assigned_vars']:
                    assign_var, _, _ = task_var['assigned_vars'][emp.idx]
                    
                    ot_var = self.model.NewIntVar(0, max_time, f'ot_e{emp.idx}_t{t_idx}')
                    
                    # overtime >= end - work_end (when assigned)
                    self.model.Add(
                        ot_var >= task_var['end'] - emp.work_end
                    ).OnlyEnforceIf(assign_var)
                    
                    # overtime >= 0 always
                    self.model.Add(ot_var >= 0)
                    
                    # overtime = 0 when not assigned to this employee
                    self.model.Add(ot_var == 0).OnlyEnforceIf(assign_var.Not())
                    
                    overtime_vars.append((
                        ot_var,
                        assign_var,
                        emp.id,
                        t_idx,
                        emp.work_end,
                        task_var['end']
                    ))
        
        variables['overtime_vars'] = overtime_vars
