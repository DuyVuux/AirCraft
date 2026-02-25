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
        # Build dependency depth map
        depth = {}
        def get_depth(t_id):
            if t_id in depth: return depth[t_id]
            t = next((x for x in self.ctx.tasks if x.id == t_id), None)
            if not t or not t.dependencies:
                depth[t_id] = 0
                return 0
            
            max_d = 0
            for d_code in t.dependencies:
                dep_t = next((x for x in self.ctx.tasks if x.aircraft_id == t.aircraft_id and x.original_task_code == d_code), None)
                if dep_t:
                    d = get_depth(dep_t.id)
                    max_d = max(max_d, d + 1)
            depth[t_id] = max_d
            return max_d

        for t in self.ctx.tasks:
            get_depth(t.id)

        sorted_tasks = sorted(
            self.ctx.tasks,
            key=lambda t: (t.latest_finish, depth[t.id], t.earliest_start)
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
        
        # 1. Dependency Check
        # Find max end time of dependencies
        dep_end_max = task.earliest_start
        for dep_code in task.dependencies:
            # Find the task ID for this dependency on the same aircraft
            dep_task = next((t for t in self.ctx.tasks if t.aircraft_id == task.aircraft_id and t.original_task_code == dep_code), None)
            if dep_task:
                if dep_task.id in solution.dropped_tasks:
                    return False  # Dependency dropped, so this must drop
                elif dep_task.id in solution.start_times:
                    # Calculate its end time
                    dep_emp_id = solution.assignments[dep_task.id]
                    dep_emp = next((e for e in self.ctx.employees if e.id == dep_emp_id), None)
                    dep_level = dep_emp.level if dep_emp else 1
                    dep_dur = self.ctx.task_level_durations.get((dep_task.id, dep_level), dep_task.duration)
                    dep_end = solution.start_times[dep_task.id] + dep_dur
                    if dep_end > dep_end_max:
                        dep_end_max = dep_end
                else:
                    # Priority sorting might have failed us, so dep not scheduled yet?
                    # This shouldn't happen if we sort correctly by dependencies.
                    pass
        
        # Iterate all employees
        for emp in self.ctx.employees:
            # 1. Capability Check
            if not all(c in emp.certs for c in task.required_certs):
                continue
            if emp.level < task.min_level:
                continue
            
            # 2. Timing Calculation
            duration = self.ctx.task_level_durations.get((task.id, emp.level), task.duration)
            if duration is None: duration = 1800 
            
            travel_time = 0
            curr_loc = self.emp_location.get(emp.id)
            if curr_loc is not None and curr_loc != task.location_idx:
                travel_time = int(self.ctx.distance_matrix[curr_loc, task.location_idx])
            
            avail = self.emp_available_time[emp.id]
            
            # Proposed start must be >= flight arrival, employee avail+travel, and all deps
            proposed_start = max(avail + travel_time, dep_end_max)
            proposed_end = proposed_start + duration
            
            # 3. Handle Constraints Interactively
            valid_assignment = False
            
            while True:
                if proposed_end > task.latest_finish:
                    break # Missed deadline completely
                
                # Check breaks overlap
                overlap_break = False
                shift_break = 0
                if emp.breaks:
                    for b_start, b_end in emp.breaks:
                        if max(proposed_start, b_start) < min(proposed_end, b_end):
                            overlap_break = True
                            shift_break = b_end
                            break
                            
                if overlap_break:
                    # Push start time to end of the break
                    # Need to recalculate travel time?
                    # If we wait at the location, we can just push start time
                    proposed_start = shift_break
                    proposed_end = proposed_start + duration
                    continue
                
                # Check Shifts bounds
                valid_shift = False
                for s_start, s_end in emp.shifts:
                    # Travel starts when employee becomes available BEFORE waiting. 
                    # But if we wait through a break, we might be at location already.
                    travel_start = max(avail, proposed_start - travel_time)
                    if travel_start >= s_start and proposed_end <= s_end:
                        valid_shift = True
                        break
                
                if not valid_shift:
                    break # Not in a valid shift
                
                valid_assignment = True
                break
                
            if not valid_assignment:
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
