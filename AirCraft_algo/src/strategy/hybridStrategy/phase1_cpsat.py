"""
Phase 1: CP-SAT Assignment Solver

Finds feasible task-employee assignments with minimal unassigned tasks.
Does not optimize timing - only finds valid assignments.
"""
import multiprocessing
from typing import Dict, List, Tuple, Any
from ortools.sat.python import cp_model

from src.strategy.orStrategy.model_builder import ModelBuilder
from src.strategy.orStrategy.constraints.assignment import AssignmentConstraint
from src.strategy.orStrategy.constraints.precedence import PrecedenceConstraint
from src.strategy.orStrategy.constraints.employee import EmployeeConstraint
from src.strategy.orStrategy.constraints.travel import TravelConstraint
from src.strategy.orStrategy.constraints.aircraft import AircraftTimeWindowConstraint


class Phase1CpSat:
    """
    Phase 1 of Hybrid Strategy: CP-SAT for assignment feasibility.
    
    Objective: Minimize number of unassigned tasks.
    Output: List of (task_idx, employee_idx) assignments.
    """
    
    def __init__(self):
        self.model = None
        self.solver = None
        self.variables = None
        
    def solve(self, data: Dict[str, Any], time_limit_seconds: int = 30) -> Tuple[bool, List[Tuple[int, int]], Dict]:
        """
        Run Phase 1 CP-SAT solver.
        
        Args:
            data: Parsed context data from OrAdapter
            time_limit_seconds: Solver time limit
            
        Returns:
            Tuple of:
            - success: True if feasible/optimal solution found
            - assignments: List of (task_idx, employee_idx) pairs
            - variables: Model variables for Phase 2 reference
        """
        builder = ModelBuilder()
        self.model, self.variables = builder.build(data)
        
        # Add constraints
        constraints = [
            AssignmentConstraint(self.model),
            PrecedenceConstraint(self.model),
            EmployeeConstraint(self.model),
            TravelConstraint(self.model),
            AircraftTimeWindowConstraint(self.model)
        ]
        
        for constraint in constraints:
            constraint.build(data, self.variables)
        
        # Simplified objective: minimize unassigned tasks only
        self._build_simplified_objective()
        
        # Create greedy hints
        self._create_greedy_hints(data)
        
        # Solve
        self.solver = cp_model.CpSolver()
        if time_limit_seconds > 0:
            self.solver.parameters.max_time_in_seconds = time_limit_seconds
        self.solver.parameters.log_search_progress = False
        self.solver.parameters.num_search_workers = max(1, multiprocessing.cpu_count() - 1)
        
        status = self.solver.Solve(self.model)
        
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            assignments = self._extract_assignments()
            return True, assignments, self.variables
        else:
            return False, [], self.variables
    
    def _build_simplified_objective(self):
        """Build objective that only minimizes unassigned tasks."""
        sum_unassigned = sum(
            tv['unassigned_var'] for tv in self.variables['tasks']
        )
        self.model.Minimize(sum_unassigned)
    
    def _create_greedy_hints(self, data: Dict[str, Any]):
        """Create greedy heuristic hints."""
        employee_available_time = {
            emp.idx: emp.work_start for emp in data['employees']
        }
        
        sorted_tasks = sorted(
            enumerate(self.variables['tasks']),
            key=lambda x: x[1]['task'].window_start
        )
        
        for t_idx, task_var in sorted_tasks:
            if not task_var['assigned_vars']:
                self.model.AddHint(task_var['unassigned_var'], 1)
                continue
            
            best_emp = None
            best_start = float('inf')
            
            for e_idx, (assign_var, duration, _) in task_var['assigned_vars'].items():
                start = max(
                    task_var['task'].window_start,
                    employee_available_time[e_idx]
                )
                
                if start + duration <= task_var['task'].window_end:
                    if start < best_start:
                        best_start = start
                        best_emp = e_idx
            
            if best_emp is not None:
                assign_var, duration, _ = task_var['assigned_vars'][best_emp]
                self.model.AddHint(assign_var, 1)
                self.model.AddHint(task_var['unassigned_var'], 0)
                self.model.AddHint(task_var['start'], best_start)
                employee_available_time[best_emp] = best_start + duration
            else:
                self.model.AddHint(task_var['unassigned_var'], 1)
    
    def _extract_assignments(self) -> List[Tuple[int, int]]:
        """Extract task-employee assignments from solved model."""
        assignments = []
        
        for t_idx, task_var in enumerate(self.variables['tasks']):
            if not self.solver.Value(task_var['unassigned_var']):
                for e_idx, (assign_var, _, _) in task_var['assigned_vars'].items():
                    if self.solver.Value(assign_var):
                        assignments.append((t_idx, e_idx))
                        break
        
        return assignments
    
    def get_start_time(self, task_idx: int) -> int:
        """Get start time for a task from Phase 1 solution."""
        return self.solver.Value(self.variables['tasks'][task_idx]['start'])
    
    def get_end_time(self, task_idx: int) -> int:
        """Get end time for a task from Phase 1 solution."""
        return self.solver.Value(self.variables['tasks'][task_idx]['end'])
