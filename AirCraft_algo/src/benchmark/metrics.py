"""
Benchmark Metrics - Data classes for benchmark results.
"""
from dataclasses import dataclass, asdict
from typing import Optional, List
import json


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    strategy_name: str
    instance_name: str
    instance_size: str
    num_tasks: int
    num_employees: int
    solve_time_ms: float
    objective_value: float
    unassigned_count: int
    assigned_count: int
    status: str
    # New metrics for optimality comparison
    is_optimal: bool = False              # Did solver prove optimality?
    lower_bound: Optional[float] = None   # Best known lower bound
    optimality_gap: Optional[float] = None  # Gap to lower bound (%)
    makespan_s: Optional[int] = None
    overtime_s: Optional[int] = None
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BenchmarkResult':
        return cls(**data)


@dataclass
class BenchmarkSummary:
    """Summary statistics across multiple runs."""
    strategy_name: str
    instance_size: str
    num_runs: int
    avg_solve_time_ms: float
    min_solve_time_ms: float
    max_solve_time_ms: float
    avg_objective: float
    avg_unassigned: float
    success_rate: float
    
    @classmethod
    def from_results(cls, results: List[BenchmarkResult]) -> 'BenchmarkSummary':
        if not results:
            raise ValueError("No results to summarize")
        
        strategy = results[0].strategy_name
        size = results[0].instance_size
        
        times = [r.solve_time_ms for r in results]
        objectives = [r.objective_value for r in results if r.status in ['OPTIMAL', 'FEASIBLE']]
        unassigned = [r.unassigned_count for r in results]
        successes = sum(1 for r in results if r.status in ['OPTIMAL', 'FEASIBLE'])
        
        return cls(
            strategy_name=strategy,
            instance_size=size,
            num_runs=len(results),
            avg_solve_time_ms=sum(times) / len(times),
            min_solve_time_ms=min(times),
            max_solve_time_ms=max(times),
            avg_objective=sum(objectives) / len(objectives) if objectives else 0,
            avg_unassigned=sum(unassigned) / len(unassigned),
            success_rate=successes / len(results)
        )
    
    def to_dict(self) -> dict:
        return asdict(self)


def results_to_json(results: List[BenchmarkResult], filepath: str):
    """Save benchmark results to JSON file."""
    data = [r.to_dict() for r in results]
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def results_from_json(filepath: str) -> List[BenchmarkResult]:
    """Load benchmark results from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return [BenchmarkResult.from_dict(d) for d in data]
