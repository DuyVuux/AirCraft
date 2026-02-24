from src.utils.logger import get_logger
logger = get_logger("src.strategy.optimization.solver")
import math
import random
import time
from typing import List, Dict, Tuple
from ortools.sat.python import cp_model
from src.strategy.optimization.models import OptimizationContext, SolutionState, OptimizationTask
from src.strategy.optimization.constraints import ConstraintProvider

from src.strategy.optimization.greedy import GreedySolver

class LNSSolver:
    def __init__(self, time_limit_seconds: int = 60, pure_cp_mode: bool = False):
        self.time_limit = time_limit_seconds
        self.pure_cp_mode = pure_cp_mode
        self.ctx = None
        self.min_temperature = 0.1

    def solve(self, ctx: OptimizationContext) -> SolutionState:
        self.ctx = ctx
        """
        Main runner for LNS.
        1. Construct initial solution (Greedy or via CP-SAT on full problem with short timeout)
        2. LNS Loop
        """
        start_time = time.time()
        
        # Phase 0: Greedy Warm Start
        logger.info("[LNS] Phase 0: Greedy Heuristic...")
        greedy_solver = GreedySolver(ctx)
        greedy_solution = greedy_solver.solve()
        logger.info(f"[LNS] Greedy found: {len(greedy_solution.assignments)} assigned, {len(greedy_solution.dropped_tasks)} dropped.")
        
        # Phase 1: Construction
        # If pure_cp_mode, spend all time here
        construction_limit = self.time_limit if self.pure_cp_mode else 5.0
        
        logger.info(f"[LNS] Phase 1: Construction (Full CP) - Time Limit: {construction_limit}s")
        # Use Greedy as HINT
        current_solution = self._solve_cp(ctx, current_solution=None, hints=greedy_solution, time_limit=construction_limit)
        
        if self.pure_cp_mode:
            return current_solution
        
        if not self._is_feasible(current_solution):
            logger.info("[LNS] Construction failed to find feasible solution. Trying fallback greedy or returning empty.")
            if self._is_feasible(greedy_solution):
                 logger.info("[LNS] Using Greedy result as fallback.")
                 current_solution = greedy_solution
            else:
                 pass
        
        best_solution = current_solution.copy()
        best_cost = self._calculate_cost(best_solution)
        
        # Phase 2: LNS Loop
        logger.info(f"[LNS] Phase 2: Loop. Start Cost: {best_cost}")
        
        temperature = 100.0
        cooling_rate = 0.99
        iteration = 0
        
        while time.time() - start_time < self.time_limit and temperature > self.min_temperature:
            iteration += 1
            
            # 1. Destroy (Ruin)
            # Pick k tasks to unassign
            # ~20% of tasks or max 20 tasks
            n_ruin = max(5, int(len(ctx.tasks) * 0.2))
            n_ruin = min(n_ruin, 30) # Cap to avoid too hard subproblem
            
            # LNS Operator Selection
            # 20% Random, 40% Spatial, 40% Worst Employment
            rand_val = random.random()
            
            if rand_val < 0.2:
                partial_solution, ruined_tasks = self._destroy_random(current_solution, ctx, n_ruin)
            elif rand_val < 0.6:
                partial_solution, ruined_tasks = self._destroy_spatial(current_solution, ctx, n_ruin)
            else:
                partial_solution, ruined_tasks = self._destroy_worst_employment(current_solution, ctx, n_ruin)
            
            # 2. Repair (Re-optimize)
            # Use CP-SAT to solve for the ruined tasks, while keeping others fixed
            new_solution = self._solve_cp(ctx, partial_solution, time_limit=2.0)
            
            # 3. Accept/Reject
            new_cost = self._calculate_cost(new_solution)
            
            # Simple Hill Climbing checking for now (or SA logic)
            if new_cost < best_cost:
                best_solution = new_solution.copy()
                best_cost = new_cost
                current_solution = new_solution
                logger.info(f"[LNS] Iter {iteration}: New Best Cost {best_cost}")
            elif self._accept_worse(current_solution, new_solution, temperature):
                current_solution = new_solution
            
            temperature *= cooling_rate
            
        return best_solution

    def _solve_cp(self, ctx: OptimizationContext, current_solution: SolutionState = None, hints: SolutionState = None, time_limit: float = 5.0) -> SolutionState:
        """
        Run CP-SAT solver.
        If current_solution is provided, fix mapped variables (Hard Constraint).
        If hints is provided, hint variables (Soft Guide).
        """
        model = cp_model.CpModel()
        cp = ConstraintProvider(model, ctx)
        cp.define_variables(0, 86400*2) # dummy horizon
        cp.add_constraints()
        
        # Objective
        model.Minimize(cp.get_objective_expr())
        
        # Hints (from Greedy)
        if hints:
            for t in ctx.tasks:
                emp_id = hints.assignments.get(t.id)
                if emp_id is not None:
                     if (t.id, emp_id) in cp.x:
                         model.AddHint(cp.x[(t.id, emp_id)], 1)
                     if t.id in cp.start:
                         model.AddHint(cp.start[t.id], hints.start_times[t.id])
        
        # Constraints from current_solution (Fixing variables for LNS)
        if current_solution:
            # For every task:
            for t in ctx.tasks:
                # If assigned in current_solution and NOT UNASSIGNED (i.e. not in ruined set)
                # Wait, 'current_solution' passed here is actually the 'partial_solution' 
                # where ruined tasks are already removed from assignments.
                
                emp_id = current_solution.assignments.get(t.id)
                start_time = current_solution.start_times.get(t.id)
                
                if emp_id is not None and start_time is not None:
                    # FIX Assignment
                    # x[t, emp] == 1
                    if (t.id, emp_id) in cp.x:
                        model.Add(cp.x[(t.id, emp_id)] == 1)
                    
                    # Fix Start Time? 
                    # If we interpret "partial solution" as "keep these tasks EXACTLY here", then fix start.
                    if t.id in cp.start:
                        model.Add(cp.start[t.id] == start_time)
                
                elif t.id in current_solution.dropped_tasks:
                     # It was explicitly dropped? 
                     # If we passed a solution where some are dropped, do we fix them as dropped?
                     # No, let solver try to re-insert if valid.
                     # But current logic is "Repair Ruined". 
                     # If it was dropped in partial, it stays dropped unless we "ruin" the dropped status.
                     # Let's fix dropped status if not ruined?
                     # Simpler: Only fix ASSIGNMENTS. Dropped tasks are free to be assigned.
                     pass
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit
        solver.parameters.log_search_progress = False
        
        status = solver.Solve(model)
        
        new_state = SolutionState()
        
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            for t in ctx.tasks:
                # Check dropped
                if solver.Value(cp.is_dropped[t.id]):
                    new_state.dropped_tasks.append(t.id)
                    continue
                
                # Check assigned
                assigned = False
                for emp in ctx.employees:
                    if (t.id, emp.id) in cp.x and solver.Value(cp.x[(t.id, emp.id)]):
                        new_state.assignments[t.id] = emp.id
                        new_state.start_times[t.id] = solver.Value(cp.start[t.id])
                        assigned = True
                        break
                
                if not assigned and t.id not in new_state.dropped_tasks:
                    # Should not match constraint?
                    pass
        else:
            # Failed to solve
            if current_solution: return current_solution
            return SolutionState() # Empty
            
        return new_state

    def _destroy_random(self, sol: SolutionState, ctx: OptimizationContext, n: int) -> Tuple[SolutionState, List[int]]:
        """Remove n tasks randomly."""
        new_sol = sol.copy()
        ruined = []
        
        # Candidates: tasks that are assigned
        assigned_ids = list(sol.assignments.keys())
        if not assigned_ids:
            return new_sol, ruined
        
        ruined = random.sample(assigned_ids, min(n, len(assigned_ids)))
        
        for tid in ruined:
            del new_sol.assignments[tid]
            del new_sol.start_times[tid]
            
        # Also could ruin dropped tasks to try inserting them
        dropped_ids = sol.dropped_tasks.copy() # copy needed?
        if dropped_ids:
             # Take some dropped tasks to re-insert
             reinsert = random.sample(dropped_ids, min(n, len(dropped_ids)))
             for tid in reinsert:
                 new_sol.dropped_tasks.remove(tid)
                 ruined.append(tid)
                 
        return new_sol, ruined

    def _destroy_spatial(self, sol: SolutionState, ctx: OptimizationContext, n: int) -> Tuple[SolutionState, List[int]]:
        """Remove tasks that are spatially close to each other."""
        new_sol = sol.copy()
        ruined = []

        assigned_ids = list(sol.assignments.keys())
        if not assigned_ids:
            return new_sol, ruined

        # 1. Pick a random center task
        center_id = random.choice(assigned_ids)
        center_task = next((t for t in ctx.tasks if t.id == center_id), None)
        
        if not center_task:
            return new_sol, ruined

        # 2. Calculate distances from center to all other assigned tasks
        distances = []
        for tid in assigned_ids:
            t = next((task for task in ctx.tasks if task.id == tid), None)
            if t:
                # Use location index to look up distance matrix
                dist = ctx.distance_matrix[center_task.location_idx, t.location_idx]
                distances.append((tid, dist))

        # 3. Sort by distance and pick nearest neighbors
        # Sort ascending (closest first)
        distances.sort(key=lambda x: x[1])
        
        # Pick top n
        candidates = [x[0] for x in distances[:n]]
        
        ruined.extend(candidates)

        # Remove from solution
        for tid in ruined:
            if tid in new_sol.assignments:
                del new_sol.assignments[tid]
                del new_sol.start_times[tid]

        return new_sol, ruined

    def _destroy_worst_employment(self, sol: SolutionState, ctx: OptimizationContext, n: int) -> Tuple[SolutionState, List[int]]:
        """
        Remove tasks from employees with the FEWEST assignments.
        Goal: Empty out an employee so they can be removed from workforce (cost redudction).
        """
        new_sol = sol.copy()
        ruined = []
        
        # 1. Count tasks per employee
        emp_task_counts = {}
        emp_task_ids = {} # emp_id -> list of task_ids
        
        for tid, emp_id in sol.assignments.items():
            emp_task_counts[emp_id] = emp_task_counts.get(emp_id, 0) + 1
            if emp_id not in emp_task_ids:
                emp_task_ids[emp_id] = []
            emp_task_ids[emp_id].append(tid)
            
        # 2. Find employees with > 0 tasks but fewest
        # Sort employees by count ascending
        sorted_emps = sorted(emp_task_counts.items(), key=lambda x: x[1])
        
        # 3. Ruin tasks from these 'worst' employees
        count_removed = 0
        for emp_id, count in sorted_emps:
            if count_removed >= n:
                break
                
            tasks_to_remove = emp_task_ids[emp_id]
            for tid in tasks_to_remove:
                if count_removed >= n:
                    break
                
                if tid in new_sol.assignments:
                    del new_sol.assignments[tid]
                    del new_sol.start_times[tid]
                    ruined.append(tid)
                    count_removed += 1
                    
        return new_sol, ruined
    
    def _calculate_cost(self, sol: SolutionState) -> float:
        dropped_penalty = len(sol.dropped_tasks) * 1_000_000

        active_employees = set(sol.assignments.values())
        headcount_penalty = len(active_employees) * 10_000

        travel_cost = 0
        if self.ctx is not None:
            emp_tasks = {}
            for task_id, emp_id in sol.assignments.items():
                if emp_id not in emp_tasks:
                    emp_tasks[emp_id] = []
                start_time = sol.start_times.get(task_id, 0)
                task = next((t for t in self.ctx.tasks if t.id == task_id), None)
                if task:
                    emp_tasks[emp_id].append((start_time, task.location_idx))

            for emp_id, task_list in emp_tasks.items():
                task_list.sort(key=lambda x: x[0])
                for i in range(len(task_list) - 1):
                    _, loc_a = task_list[i]
                    _, loc_b = task_list[i + 1]
                    if loc_a != loc_b:
                        tt = self.ctx.distance_matrix[loc_a, loc_b]
                        if not math.isinf(tt):
                            travel_cost += int(tt)

        return dropped_penalty + headcount_penalty + travel_cost

    def _is_feasible(self, sol: SolutionState) -> bool:
        """Check if solution has any content."""
        return len(sol.assignments) > 0 or len(sol.dropped_tasks) > 0

    def _accept_worse(self, current: SolutionState, candidate: SolutionState, temp: float) -> bool:
        current_cost = self._calculate_cost(current)
        candidate_cost = self._calculate_cost(candidate)
        delta = candidate_cost - current_cost
        if delta <= 0:
            return True
        if temp <= 0:
            return False
        probability = math.exp(-delta / temp)
        return random.random() < probability
