"""
Benchmark Runner - Execute and compare solver strategies.
"""
import time
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from src.model.context import Context
from src.model.solution import Solution
from src.strategy import IStrategy
from src.strategy.orStrategy import OrStrategy
from src.strategy.hybridStrategy import HybridStrategy
from .metrics import BenchmarkResult, BenchmarkSummary
from .generator import InstanceGenerator


# Available strategies (using basic domain reduction only - no heuristic filtering)
STRATEGY_REGISTRY = {
    'cpsat': lambda tl: OrStrategy(time_limit_seconds=tl),
    'hybrid': lambda tl: HybridStrategy(time_limit_seconds=tl)
}


def count_tasks(context: Context) -> int:
    """Count total tasks across all aircrafts."""
    return sum(len(ac.requiredTasks) for ac in context.aircrafts)


class BenchmarkRunner:
    """
    Run benchmarks comparing different solver strategies.
    """
    
    def __init__(self, time_limit_seconds: int = 30):
        self.time_limit_seconds = time_limit_seconds
        self.generator = InstanceGenerator()
        self.results: List[BenchmarkResult] = []
    
    def run_single(self, strategy_name: str, context: Context,
                   instance_name: str, instance_size: str) -> BenchmarkResult:
        """
        Run a single benchmark.
        
        Args:
            strategy_name: Name of strategy ('cpsat' or 'hybrid')
            context: The problem context
            instance_name: Name of the instance
            instance_size: Size category ('small', 'medium', 'large')
            
        Returns:
            BenchmarkResult with metrics
        """
        if strategy_name not in STRATEGY_REGISTRY:
            return BenchmarkResult(
                strategy_name=strategy_name,
                instance_name=instance_name,
                instance_size=instance_size,
                num_tasks=count_tasks(context),
                num_employees=len(context.employees),
                solve_time_ms=0,
                objective_value=0,
                unassigned_count=0,
                assigned_count=0,
                status='ERROR',
                error=f"Unknown strategy: {strategy_name}"
            )
        
        # Create strategy
        strategy = STRATEGY_REGISTRY[strategy_name](self.time_limit_seconds)
        strategy.init(context)
        
        # Time the solve
        start_time = time.time()
        error = None
        solution = None
        is_optimal = False
        lower_bound = None
        solver_objective = None
        
        try:
            solution = strategy.execute()
            status = 'FEASIBLE' if solution and solution.employees else 'INFEASIBLE'
            
            # Check for optimal and get objective from OrStrategy
            if hasattr(strategy, 'solver') and strategy.solver:
                from ortools.sat.python import cp_model
                solver = strategy.solver
                solver_status = strategy.status if hasattr(strategy, 'status') else None
                
                if solver_status == cp_model.OPTIMAL:
                    status = 'OPTIMAL'
                    is_optimal = True
                    solver_objective = solver.ObjectiveValue()
                    lower_bound = solver.BestObjectiveBound()
                elif solver_status == cp_model.FEASIBLE:
                    solver_objective = solver.ObjectiveValue()
                    lower_bound = solver.BestObjectiveBound()
            
            # Check for HybridStrategy metrics
            if hasattr(strategy, 'get_metrics'):
                metrics = strategy.get_metrics()
                if metrics.get('phase1_status') == 'FEASIBLE' and metrics.get('used_phase2'):
                    # Hybrid found solution
                    if metrics.get('phase2_status') == 'OPTIMAL':
                        is_optimal = True
                        status = 'OPTIMAL'
                        
        except Exception as e:
            status = 'ERROR'
            error = str(e)
            solution = None
        
        solve_time_ms = (time.time() - start_time) * 1000
        
        # Extract metrics from solution
        if solution:
            assigned_count = sum(
                len(emp.assignments) for emp in solution.employees
            )
            unassigned_count = sum(len(d.tasks) for d in solution.droppedTasks)
            
            # Calculate makespan (latest end time)
            makespan = 0
            for emp in solution.employees:
                for asg in emp.assignments:
                    from src.model.time import parse_time
                    end_ts = parse_time(asg.endTime)
                    makespan = max(makespan, end_ts)
            
            # Use solver objective if available, otherwise approximate
            if solver_objective is not None:
                objective_value = solver_objective
            else:
                objective_value = unassigned_count * 10000000 + makespan
        else:
            assigned_count = 0
            unassigned_count = count_tasks(context)
            makespan = 0
            objective_value = float('inf')
        
        # Calculate optimality gap
        optimality_gap = None
        if lower_bound is not None and objective_value > 0 and objective_value != float('inf'):
            if lower_bound > 0:
                optimality_gap = round((objective_value - lower_bound) / lower_bound * 100, 2)
            else:
                optimality_gap = 0.0
        
        return BenchmarkResult(
            strategy_name=strategy_name,
            instance_name=instance_name,
            instance_size=instance_size,
            num_tasks=count_tasks(context),
            num_employees=len(context.employees),
            solve_time_ms=round(solve_time_ms, 2),
            objective_value=objective_value,
            unassigned_count=unassigned_count,
            assigned_count=assigned_count,
            status=status,
            is_optimal=is_optimal,
            lower_bound=lower_bound,
            optimality_gap=optimality_gap,
            makespan_s=makespan if makespan > 0 else None,
            error=error
        )
    
    def run_comparison(self, strategies: List[str] = None,
                       sizes: List[str] = None,
                       num_instances: int = 1) -> List[BenchmarkResult]:
        """
        Run comparison benchmark across strategies and sizes.
        
        Args:
            strategies: List of strategy names (default: ['cpsat', 'hybrid'])
            sizes: List of sizes (default: ['small', 'medium'])
            num_instances: Number of instances per size
            
        Returns:
            List of BenchmarkResults
        """
        if strategies is None:
            strategies = ['cpsat', 'hybrid']
        if sizes is None:
            sizes = ['small', 'medium']
        
        self.results = []
        
        print(f"\n{'='*60}")
        print(f"BENCHMARK: {strategies} on {sizes}")
        print(f"{'='*60}\n")
        
        for size in sizes:
            for instance_id in range(num_instances):
                # Generate instance
                instance_name = f"{size}_{instance_id}"
                print(f"[Instance] {instance_name}")
                
                context = self.generator.generate_context(size, instance_id)
                num_tasks = count_tasks(context)
                num_employees = len(context.employees)
                print(f"  Tasks: {num_tasks}, Employees: {num_employees}")
                
                for strategy_name in strategies:
                    print(f"  Running {strategy_name}...", end=' ', flush=True)
                    
                    result = self.run_single(
                        strategy_name, context, instance_name, size
                    )
                    self.results.append(result)
                    
                    print(f"{result.status} in {result.solve_time_ms:.0f}ms "
                          f"(assigned: {result.assigned_count}/{num_tasks})")
        
        print(f"\n{'='*60}")
        print(f"COMPLETED: {len(self.results)} benchmark runs")
        print(f"{'='*60}\n")
        
        return self.results
    
    def get_summary(self) -> Dict[str, List[BenchmarkSummary]]:
        """Get summary statistics grouped by strategy."""
        from collections import defaultdict
        
        grouped = defaultdict(lambda: defaultdict(list))
        for result in self.results:
            grouped[result.strategy_name][result.instance_size].append(result)
        
        summaries = {}
        for strategy, sizes in grouped.items():
            summaries[strategy] = [
                BenchmarkSummary.from_results(results)
                for size, results in sizes.items()
            ]
        
        return summaries
    
    def print_summary(self):
        """Print benchmark summary to console."""
        summaries = self.get_summary()
        
        print("\n" + "="*80)
        print("BENCHMARK SUMMARY")
        print("="*80)
        
        for strategy, size_summaries in summaries.items():
            print(f"\n[{strategy.upper()}]")
            for summary in size_summaries:
                print(f"  {summary.instance_size}: "
                      f"avg={summary.avg_solve_time_ms:.0f}ms, "
                      f"success={summary.success_rate*100:.0f}%, "
                      f"unassigned={summary.avg_unassigned:.1f}")
        
        print("\n" + "="*80)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary for JSON serialization."""
        return {
            'results': [r.to_dict() for r in self.results],
            'summary': {
                strategy: [s.to_dict() for s in summaries]
                for strategy, summaries in self.get_summary().items()
            }
        }
