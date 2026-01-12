"""
OR-Tools Strategy - Main orchestrator for OR-Tools optimization.
"""
import multiprocessing
from typing import Optional
from ortools.sat.python import cp_model

from src.model.context import Context
from src.model.solution import Solution
from src.strategy.base import IStrategy
from src.strategy.adapters import OrAdapter
from src.strategy.orStrategy.model_builder import ModelBuilder
from src.strategy.orStrategy.objective_builder import ObjectiveBuilder, print_penalty_breakdown
from src.strategy.orStrategy.constraints.assignment import AssignmentConstraint
from src.strategy.orStrategy.constraints.precedence import PrecedenceConstraint
from src.strategy.orStrategy.constraints.employee import EmployeeConstraint
from src.strategy.orStrategy.constraints.travel import TravelConstraint
from src.strategy.orStrategy.constraints.aircraft import AircraftTimeWindowConstraint
from src.strategy.orStrategy.constraints.bus import BusConstraint


class OrStrategy(IStrategy):
    """
    OR-Tools CP-SAT based optimization strategy.
    
    Orchestrates:
    1. Data conversion via OrAdapter
    2. Model and variable creation via ModelBuilder
    3. Constraint building via constraint components
    4. Objective function via ObjectiveBuilder
    5. Solving and solution extraction
    """
    
    def __init__(self, time_limit_seconds: int = 60):
        """
        Initialize OR-Tools strategy.
        
        Args:
            time_limit_seconds: Solver time limit
        """
        super().__init__()
        self.time_limit_seconds = time_limit_seconds
        
        self.adapter = OrAdapter()
        self.model = None
        self.solver = None
        self._status = None  # Track solve status
    
    @property
    def is_optimal(self) -> bool:
        """Check if solution is optimal."""
        from ortools.sat.python import cp_model
        return self._status == cp_model.OPTIMAL
    
    def execute(self) -> Solution:
        """
        Execute OR-Tools optimization strategy.
        
        Returns:
            Optimized solution or empty solution if infeasible
        """
        # 1. Adapt input: Context → OR-Tools internal data
        data = self.adapter.adapt_input(self.context)
        
        # 2. Build model and variables
        builder = ModelBuilder()
        model, variables = builder.build(data)
        self.model = model
        
        # 3. Add constraints
        constraints = [
            AssignmentConstraint(model),
            PrecedenceConstraint(model),
            EmployeeConstraint(model),
            TravelConstraint(model),
            AircraftTimeWindowConstraint(model),
            BusConstraint(model)  # NEW: Bus travel constraints
        ]
        
        for constraint in constraints:
            result = constraint.build(data, variables)
            # Store bus variables for objective builder
            if isinstance(constraint, BusConstraint) and result:
                variables['bus_vars'] = result
        
        # 4. Build objective
        self.objective_builder = ObjectiveBuilder(model)
        self.objective_builder.build(data, variables)
        
        # 5. Add hints
        if self.solution and self.solution.employees:
            # Use provided initial solution as hints
            self._apply_solution_hints(model, variables, data, self.solution)
        else:
            # Use greedy heuristic
            self._create_greedy_hints(model, variables, data)
        
        # 6. Solve
        self.solver = cp_model.CpSolver()
        if self.time_limit_seconds > 0:
            self.solver.parameters.max_time_in_seconds = self.time_limit_seconds
        self.solver.parameters.log_search_progress = False
        self.solver.parameters.num_search_workers = max(1, multiprocessing.cpu_count() - 1)
        
        status = self.solver.Solve(model)
        self._status = status  # Save for is_optimal property
        
        # Print status
        status_names = {
            cp_model.OPTIMAL: 'OPTIMAL',
            cp_model.FEASIBLE: 'FEASIBLE',
            cp_model.INFEASIBLE: 'INFEASIBLE',
            cp_model.MODEL_INVALID: 'MODEL_INVALID',
            cp_model.UNKNOWN: 'UNKNOWN'
        }
        print(f"\n[OrStrategy] Status: {status_names.get(status, 'UNKNOWN')}")
        
        # Print penalty breakdown
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            breakdown = self.objective_builder.get_penalty_breakdown(self.solver)
            print_penalty_breakdown(breakdown)
        
        # 7. Extract solution
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            internal_result = {
                'solver': self.solver,
                'variables': variables,
                'data': data
            }
            return self.adapter.adapt_output(internal_result, self.context)
        else:
            return Solution.empty()
    
    def _apply_solution_hints(self, model: cp_model.CpModel, variables: dict, 
                              data: dict, solution: Solution) -> None:
        """Apply hints from existing solution."""
        # Convert solution to task assignments map
        task_assignments = {}
        task_times = {}
        
        for emp_solution in solution.employees:
            emp_id = emp_solution.employeeId
            for assignment in emp_solution.assignments:
                task_id = f"{assignment.aircraftId}_{assignment.taskCode}"
                task_assignments[task_id] = emp_id
                task_times[task_id] = (assignment.startTime, assignment.endTime)
        
        # Map employee IDs to indices
        emp_id_to_idx = {emp.id: emp.idx for emp in data['employees']}
        
        for task_var in variables['tasks']:
            task_id = task_var['task'].id
            
            if task_id in task_assignments:
                emp_id = task_assignments[task_id]
                emp_idx = emp_id_to_idx.get(emp_id)
                
                if emp_idx is not None and emp_idx in task_var['assigned_vars']:
                    # Hint assignment
                    assign_var, _, _ = task_var['assigned_vars'][emp_idx]
                    model.AddHint(assign_var, 1)
                    model.AddHint(task_var['unassigned_var'], 0)
                    
                    # Hint times
                    if task_id in task_times:
                        start_iso, end_iso = task_times[task_id]
                        from src.strategy.adapters.or_adapter import parse_time, normalize_time
                        
                        start_ts = normalize_time(parse_time(start_iso), data['min_global_time'])
                        model.AddHint(task_var['start'], start_ts)
    
    def _create_greedy_hints(self, model: cp_model.CpModel,
                            variables: dict, data: dict) -> None:
        """Create greedy heuristic hints."""
        # Track employee availability
        employee_available_time = {
            emp.idx: emp.work_start for emp in data['employees']
        }
        
        # Sort tasks by window start
        sorted_tasks = sorted(
            enumerate(variables['tasks']),
            key=lambda x: x[1]['task'].window_start
        )
        
        for t_idx, task_var in sorted_tasks:
            if not task_var['assigned_vars']:
                model.AddHint(task_var['unassigned_var'], 1)
                continue
            
            best_emp = None
            best_start = float('inf')
            
            # Find earliest available employee
            for e_idx, (assign_var, duration, _) in task_var['assigned_vars'].items():
                start = max(
                    task_var['task'].window_start,
                    employee_available_time[e_idx]
                )
                
                # Check if fits in window
                if start + duration <= task_var['task'].window_end:
                    if start < best_start:
                        best_start = start
                        best_emp = e_idx
            
            if best_emp is not None:
                # Hint assignment
                assign_var, duration, _ = task_var['assigned_vars'][best_emp]
                model.AddHint(assign_var, 1)
                model.AddHint(task_var['unassigned_var'], 0)
                model.AddHint(task_var['start'], best_start)
                
                # Update availability
                employee_available_time[best_emp] = best_start + duration
            else:
                model.AddHint(task_var['unassigned_var'], 1)
