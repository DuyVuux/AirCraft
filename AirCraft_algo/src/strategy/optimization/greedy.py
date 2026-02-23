from typing import List, Dict, Tuple, Optional, Set
import math
from src.strategy.optimization.models import OptimizationContext, OptimizationTask, OptimizationEmployee, SolutionState

class GreedySolver:
    """
    Constructive Heuristic working on OptimizationContext (Integer-based).
    """
    
    def __init__(self, ctx: OptimizationContext):
        self.ctx = ctx
        # State tracking
        self.emp_available_time = {} # emp_id -> int (timestamp)
        self.emp_location = {}       # emp_id -> int (location_idx)
        
        # Initialize state
        for emp in ctx.employees:
            # Init available time to start of first shift (or 0)
            if emp.shifts:
                self.emp_available_time[emp.id] = emp.shifts[0][0]
            else:
                self.emp_available_time[emp.id] = 0
            
            self.emp_location[emp.id] = emp.start_location_idx

    def solve(self) -> SolutionState:
        solution = SolutionState()
        
        # 1. Sort tasks
        # Criteria: Deadline ASC, Priority (ARR < TOW < WO < DEP)
        # Priority mapping
        def get_priority(code: str) -> int:
            if 'ARR' in code: return 0
            if 'TOW' in code: return 1
            if 'DEP' in code: return 3
            return 2
            
        sorted_tasks = sorted(
            self.ctx.tasks,
            key=lambda t: (t.latest_finish, get_priority(t.original_task_code))
        )
        
        # 2. Assign
        for task in sorted_tasks:
            assigned = self._assign_task(task, solution)
            if not assigned:
                solution.dropped_tasks.append(task.id)
                
        return solution

    def _assign_task(self, task: OptimizationTask, solution: SolutionState) -> bool:
        best_emp_id = None
        best_start = float('inf')
        best_end = float('inf')
        
        # Iterate all employees
        for emp in self.ctx.employees:
            # 1. Capability Check
            # Certs
            if not all(c in emp.certs for c in task.required_certs):
                continue
            # Level
            if emp.level < task.min_level:
                continue
            
            # 2. Timing Calculation
            # Duration (Level based)
            duration = self.ctx.task_level_durations.get((task.id, emp.level), task.duration)
            if duration is None:
                 # Should not happen given fallbacks
                 duration = 1800 
            
            # Travel Time
            # From emp location to task location
            travel_time = 0
            curr_loc = self.emp_location.get(emp.id)
            if curr_loc is not None:
                # Assuming task location is fixed (aircraft location)
                # Task location is in task.location_idx
                if curr_loc != task.location_idx:
                    travel_time = int(self.ctx.distance_matrix[curr_loc, task.location_idx])
            
            # Earliest possible start
            # max(Task Earliest Start, Emp Available + Travel)
            # Also must be AFTER aircraft arrival? Task Earliest Start handles this.
            
            avail = self.emp_available_time[emp.id]
            
            proposed_start = max(task.earliest_start, avail + travel_time)
            proposed_end = proposed_start + duration
            
            # 3. Constraints Check
            # a. Task Deadline (Warning: Using Soft Deadline logic? Or Hard?)
            # Greedy should try to respect Hard constraints first.
            # Latest Finish = Aircraft Departure (usually).
            if proposed_end > task.latest_finish:
                continue
            
            # b. Employee Shift
            # Find shift that covers [start, end]
            valid_shift = False
            for s_start, s_end in emp.shifts:
                # Travel happens inside shift? Usually yes.
                # Travel starts at 'avail'.
                # Task starts at 'proposed_start'.
                # Work ends at 'proposed_end'.
                # So Shift must cover [avail, proposed_end]? 
                # Or just [proposed_start, proposed_end]?
                # Safest: Shift must cover work. Travel can be before?
                # Usually travel is paid time -> must be in shift.
                # Travel start = proposed_start - travel_time.
                travel_start = proposed_start - travel_time
                if travel_start >= s_start and proposed_end <= s_end:
                    valid_shift = True
                    break
            
            if not valid_shift:
                continue

            # c. Fixed Breaks
            # Check overlap
            # Interval: [proposed_start, proposed_end]
            overlap_break = False
            if emp.breaks:
                for b_start, b_end in emp.breaks:
                     if max(proposed_start, b_start) < min(proposed_end, b_end):
                         overlap_break = True
                         break
            if overlap_break:
                continue

            # 4. Optimization (Earliest Completion)
            if proposed_end < best_end:
                best_end = proposed_end
                best_start = proposed_start
                best_emp_id = emp.id
        
        if best_emp_id is not None:
            # Assign
            solution.assignments[task.id] = best_emp_id
            solution.start_times[task.id] = best_start
            
            # Update State
            self.emp_available_time[best_emp_id] = best_end
            self.emp_location[best_emp_id] = task.location_idx
            return True
            
        return False
