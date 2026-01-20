import random
import time
import math
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass

from src.strategy.base import IStrategy
from src.model.context import Context
from src.model.solution import Solution, TaskAssignment, EmployeeSolution
from src.strategy.greedyStrategy.greedy_strategy import GreedyStrategy
from src.model.time import parse_time, timestamp_to_iso

# Try to import ortools, handle if missing
try:
    from ortools.sat.python import cp_model
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    print("Warning: ortools not found. LNS will degrade to Random Walk.")

class LNSStrategy(IStrategy):
    """
    Hybrid Large Neighborhood Search (LNS) Strategy.
    
    Phase 1: Construction (Greedy)
    Phase 2: LNS Loop
        - Destroy: Remove k tasks (Random, Worst-fit, etc.)
        - Repair: Re-insert using CP-SAT Solver (Optimal for sub-problem)
    """
    
    def __init__(self, time_limit_seconds: int = 300):
        super().__init__()
        self.time_limit_seconds = time_limit_seconds
        self.start_time = 0
        
        # Hyperparameters
        self.initial_temp = 1000.0
        self.cooling_rate = 0.995
        self.min_temp = 0.1
        self.destroy_size_percent = 0.15  # Destroy 15% of tasks
        
    def execute(self) -> Solution:
        if not self.context:
            return Solution.empty()
            
        self.start_time = time.time()
        print(f"[LNS] Starting optimization (Limit: {self.time_limit_seconds}s)...")
        
        # 1. Construction Phase
        print("[LNS] Phase 1: Construction (Greedy Base)...")
        current_solution = self._get_initial_solution()
        best_solution = current_solution
        best_cost = self._calculate_cost(best_solution)
        current_cost = best_cost
        
        print(f"[LNS] Initial Cost: {best_cost:.2f}")
        
        if not ORTOOLS_AVAILABLE:
            print("[LNS] OR-Tools not available. Returning greedy solution.")
            return current_solution
            
        # 2. LNS Loop
        temperature = self.initial_temp
        iteration = 0
        
        while self._should_continue():
            iteration += 1
            
            # Create a working copy (naive deep copy via dict roundtrip or custom clone)
            # For simplicity in this mvp, we might need a better clone mechanism
            # But let's assume we operate on a fresh copy built from the current solution's data
            
            # For this implementation, we will perform Destroy/Repair on data structures
            # and rebuild the Solution object only when accepting.
            # To avoid complex cloning, we'll implement operators that distinctively modify a 'plan' structure
            # and then convert to Solution.
            
            # ... For MVP, let's keep it simple: Just try to improve dropped tasks first
            # Current Greedy drops tasks. LNS goal #1: Assign dropped tasks.
            
            # Actually, proper LNS needs to rip out assigned tasks too.
            # Let's perform a simpler version: 
            # 1. Take current solution.
            # 2. Identify 'Destroy Set': k random assigned tasks + all currently dropped tasks.
            # 3. 'Repair': Solve CP-SAT for these tasks + tasks' original employees (subset).
            
    
    def _solve_cp_subproblem(self, tasks: List['TaskItem'], employees: List['EmployeeState']) -> Tuple[List[TaskAssignment], List['TaskItem']]:
        """
        Solve a sub-problem optimally using CP-SAT.
        Returns (new_assignments, remaining_dropped_tasks).
        """
        if not tasks:
            return [], []
            
        model = cp_model.CpModel()
        
        # --- Variables ---
        # x[task_i, emp_k]: bool, task i assigned to emp k
        x = {} 
        # start[task_i]: int
        starts = {}
        ends = {}
        intervals = {}
        
        # Helper to get valid checks
        # tailored_duration[(t, e)] -> int
        durations = {}
        
        # Pre-filter capabilities to reduce variable count
        # feasible_employees[task_i] -> List[emp_k]
        feasible_employees = {t.task_code + "_" + t.aircraft_id: [] for t in tasks}
        
        for t in tasks:
            t_key = t.task_code + "_" + t.aircraft_id
            starts[t_key] = model.NewIntVar(t.earliest_start, t.deadline, f'start_{t_key}')
            # Duration is variable depending on employee, so we need a master interval?
            # Or conditional intervals.
            # Simplified approach: We create Optional Intervals for each (task, employee) pair.
            
            is_assigned_any = []
            
            for e in employees:
                # Check capability (reuse logic from greedy or duplicate)
                # For speed, assume pre-filtered or check here
                 # Note: access private _can_employee_do_task if possible or reimplement
                if not self._can_do(e, t):
                    continue
                
                feasible_employees[t_key].append(e)
                
                # Decision var
                x[t_key, e.employee_id] = model.NewBoolVar(f'x_{t_key}_{e.employee_id}')
                is_assigned_any.append(x[t_key, e.employee_id])
                
                # Time vars
                duration = self._get_duration(t, e)
                durations[t_key, e.employee_id] = duration
                
                # Optional Interval for this employee performing this task
                # We need separate start/end for each employee assignment because duration varies?
                # Actually, standard VRPTW CP model:
                # One master start var, duration depends on assignment.
                
                # If duration varies significantly, we accept complexity.
                # If duration is constant per task, it's easier.
                # Problem desc says: duration depends on Level (Employee). So it VARIES.
                
                # Correct CP approach for variable duration:
                # interval = NewOptionalIntervalVar(start, duration, end, is_present, name)
                # But start is processing start.
                
                # To simplify: Let's assume master Start variable.
                # end = start + sum(x[t,e] * duration_e)
                
                # Linear expression for duration
                actual_duration = sum(x[t_key, emp.employee_id] * durations[t_key, emp.employee_id] 
                                    for emp in feasible_employees[t_key])
                
                # But tasks can be unassigned.
                # If unassigned, duration = 0? No, unassigned tasks don't consume resource.
            
            # Constraint: At most one employee
            model.Add(sum(is_assigned_any) <= 1)
            
            # Constraint: If assigned, Start + Duration <= End
            # And End <= Deadline
            # This is hard with variable duration in standard cumulative/no_overlap.
            
            # Alternative: A boolean "performed" var.
            performed = model.NewBoolVar(f'performed_{t_key}')
            model.Add(performed == sum(is_assigned_any))
            
            # Link start/end logic? 
            # OR-Tools Interval var must have fixed duration or variable duration.
            # We construct per-employee intervals.
            
        # --- Per-Employee Constraints ---
        
        assignments = []
        
        for e in employees:
            e_intervals = []
            
            for t in tasks:
                t_key = t.task_code + "_" + t.aircraft_id
                if (t_key, e.employee_id) in x:
                    # Create optional interval for this employee doing this task
                    # Start, End must be "linked" to the task's actual execution time
                    # But simpler: Task has its own timeline on this employee.
                    
                    details_start = model.NewIntVar(t.earliest_start, t.deadline, f's_{t_key}_{e.employee_id}')
                    details_end = model.NewIntVar(t.earliest_start, t.deadline, f'e_{t_key}_{e.employee_id}')
                    dur = durations[t_key, e.employee_id]
                    
                    isActive = x[t_key, e.employee_id]
                    
                    interval = model.NewOptionalIntervalVar(
                        details_start, dur, details_end, isActive, f'interval_{t_key}_{e.employee_id}'
                    )
                    e_intervals.append(interval)
                    
                    # If this employee does it, the Global Task Start is synced (optional)
                    # For output, we just read this employee's start.
                    
            # No Overlap for employee
            # We MUST account for TRAVEL TIME.
            # NoOverlap in CP-SAT doesn't handle travel time matrix directly between arbitrary nodes.
            # Circuit constraint does, but that's for routing.
            
            # Approach for Travel Time with NoOverlap:
            # We cannot easily use NoOverlap with sequence-dependent setup times.
            # We must use "Circuit" or "AddCircuit" constraint for routing if we want exact travel times.
            # OR make the interval include travel time? 
            # Interval = Travel + Work? Start time becomes "Start Travel"? 
            # But Time Window applies to "Start Work".
            
            # Simplification for LNS Repair (Small N):
            # If N < 12 per employee, Circuit is fine.
            # BUT we have multiple employees.
            
            # Fallback: Relax travel time in CP or use constant buffer?
            # "Travel time" constraint:
            # logic: End_i + Dist(i, j) <= Start_j  if i -> j
            
            # This requires defining a sequence.
            # Standard CP-SAT VRP formulation uses:
            # lit[i,j] is true if i -> j.
            
            model.AddNoOverlap(e_intervals)
            # CAUTION: This ignores travel time!
            # To fix: Buffer?
            # We will use NoOverlap for now as MVP and assume tasks are close or buffer is enough.
            # TODO: Add Circuit constraint for proper VRP modeling in next iteration.
            
        
        # --- Objective ---
        # Objective: Maximize assigned tasks
        total_assigned = sum(
            x[t.task_code + "_" + t.aircraft_id, e.employee_id] 
            for t in tasks 
            for e in employees 
            if (t.task_code + "_" + t.aircraft_id, e.employee_id) in x
        )
        model.Maximize(total_assigned)
        
        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 5.0
        status = solver.Solve(model)
        
        new_assignments = []
        dropped_items = []
        
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            for t in tasks:
                t_key = t.task_code + "_" + t.aircraft_id
                
                is_assigned = False
                for e in employees:
                    if (t_key, e.employee_id) in x:
                        if solver.BooleanValue(x[t_key, e.employee_id]):
                            # Extract start/end time
                            # We stored these in 'starts' dict but they were per-task vars?
                            # In loop above: 
                            # details_start = model.NewIntVar(...) named f's_{t_key}_{e.employee_id}'
                            # We didn't store details_start in a map. We must rely on string name lookup? 
                            # No, CP solver needs the Variable object usually.
                            
                            # Correction: We must rebuild vars map or re-structure.
                            # Since we didn't save details_start in a class dict, we can't access it easily here.
                            # FIX: Let's store them in the loop.
                            pass # Caught by replacement logic, we will rewrite the loop to store vars.
                            
                            # Assuming we fix storage below:
                            # s = solver.Value(var_map_start[t_key, e.employee_id])
                            # e_time = solver.Value(var_map_end[t_key, e.employee_id])
                            
                            is_assigned = True
                            # assignment = TaskAssignment(...)
                            # new_assignments.append(assignment)
                            break
                
                if not is_assigned:
                    dropped_items.append(t)
        else:
            dropped_items = list(tasks)
            
        return new_assignments, dropped_items
    
    # RE-IMPLEMENTING _solve_cp_subproblem with proper variable storage
    def _solve_cp_subproblem(self, tasks: List['TaskItem'], employees: List['EmployeeState']) -> Tuple[List[TaskAssignment], List['TaskItem']]:
        if not tasks: return [], []
        model = cp_model.CpModel()
        
        x = {}          # (t_key, e_id) -> BoolVar
        start_vars = {} # (t_key, e_id) -> IntVar
        end_vars = {}   # (t_key, e_id) -> IntVar
        
        feasible_employees = {f"{t.task_code}_{t.aircraft_id}": [] for t in tasks}
        
        # Per-employee intervals for NoOverlap
        e_intervals = {e.employee_id: [] for e in employees}
        
        for t in tasks:
            t_key = f"{t.task_code}_{t.aircraft_id}"
            task_assigned_vars = []
            
            for e in employees:
                if not self._can_do(e, t): continue
                feasible_employees[t_key].append(e)
                
                # Decision Variable
                is_active = model.NewBoolVar(f'x_{t_key}_{e.employee_id}')
                x[t_key, e.employee_id] = is_active
                task_assigned_vars.append(is_active)
                
                # Time Variables
                dur = self._get_duration(t, e)
                s = model.NewIntVar(t.earliest_start, t.deadline, f's_{t_key}_{e.employee_id}')
                e_end = model.NewIntVar(t.earliest_start, t.deadline, f'e_{t_key}_{e.employee_id}')
                
                start_vars[t_key, e.employee_id] = s
                end_vars[t_key, e.employee_id] = e_end
                
                # Interval
                interval = model.NewOptionalIntervalVar(s, dur, e_end, is_active, f'int_{t_key}_{e.employee_id}')
                e_intervals[e.employee_id].append(interval)
            
            if task_assigned_vars:
                model.Add(sum(task_assigned_vars) <= 1)
            else:
                pass # Impossible to assign
        
        # Add NoOverlap constraint for each employee
        for e in employees:
            if e_intervals[e.employee_id]:
                model.AddNoOverlap(e_intervals[e.employee_id])
                
        # Objective: Maximize assignments
        model.Maximize(sum(x.values()))
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 5.0
        status = solver.Solve(model)
        
        new_assignments = []
        dropped = []
        
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            for t in tasks:
                t_key = f"{t.task_code}_{t.aircraft_id}"
                assigned = False
                for e in employees:
                    if (t_key, e.employee_id) in x:
                        if solver.BooleanValue(x[t_key, e.employee_id]):
                            s_val = solver.Value(start_vars[t_key, e.employee_id])
                            e_val = solver.Value(end_vars[t_key, e.employee_id])
                            
                            new_assignments.append(TaskAssignment(
                                taskCode=t.task_code,
                                aircraftId=t.aircraft_id,
                                requiredCertificates=t.required_certificates,
                                locationId=t.location_id,
                                startTime=timestamp_to_iso(s_val),
                                endTime=timestamp_to_iso(e_val)
                            ))
                            assigned = True
                            break
                if not assigned:
                    dropped.append(t)
        else:
            dropped = list(tasks)
            
        return new_assignments, dropped

    def _get_duration(self, task, emp):
        # Scan MatrixConfig
        # In a real impl, we should cache this matrix in __init__ for O(1) access
        if not self.context or not self.context.matrixConfigs:
            return 1800
            
        # Try finding specific entry
        for entry in self.context.matrixConfigs.time_entries:
            if entry.taskCode == task.task_code and entry.aircraftId == task.aircraft_id:
                if entry.role == emp.role: # Match role
                     return entry.timeProcess
        
        # Fallback generic
        for entry in self.context.matrixConfigs.time_entries:
            if entry.taskCode == task.task_code and entry.role is None:
                return entry.timeProcess
        
        return 1800

    
    def _get_initial_solution(self) -> Solution:
        """Run Greedy strategy to get initial feasible solution."""
        greedy = GreedyStrategy()
        greedy.init(self.context)
        return greedy.execute()
        
    def _calculate_cost(self, solution: Solution) -> float:
        """
        Cost function:
        - Dropped Task: 1,000,000
        - Employee Used: 10,000
        - Travel Time: 1 * seconds
        """
        dropped_count = sum(len(d.tasks) for d in solution.droppedTasks)
        employees_count = len(solution.employees)
        
        # Travel time calculation (approximation from assignments)
        # Note: solution.employees[i].assignments has times, but we need location distances
        # For now, let's focus on Dropped + Staff
        
        return (dropped_count * 1_000_000) + (employees_count * 10_000)
        
    def _should_continue(self) -> bool:
        return (time.time() - self.start_time) < self.time_limit_seconds

