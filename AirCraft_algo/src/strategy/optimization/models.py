from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import numpy as np

@dataclass
class OptimizationTask:
    """Internal integer-mapped representation of a Task instance."""
    id: int  # Internal index 0..N-1
    original_task_code: str
    aircraft_id: str
    
    # Time Window
    earliest_start: int
    latest_finish: int
    duration: int
    
    # Location
    location_idx: int
    
    # Requirements
    required_certs: List[int]  # Mapped indices of certificates
    
    # V2: Level and Dependencies
    min_level: int = 1
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class OptimizationEmployee:
    """Internal integer-mapped representation of an Employee."""
    id: int  # Internal index 0..M-1
    original_id: str
    
    # Capabilities (mapped indices)
    certs: set[int]  # Fast lookup
    
    # Availability (list of [start, end] intervals)
    shifts: List[Tuple[int, int]]
    
    # Base location
    start_location_idx: Optional[int] = None
    
    # V2: Level System
    level: int = 1
    
    # V2: Fixed Break Times (list of [start, end] intervals) 
    breaks: List[Tuple[int, int]] = None
    
    def __post_init__(self):
        if self.breaks is None:
            self.breaks = []


@dataclass
class OptimizationContext:
    """Read-only context for the solver."""
    tasks: List[OptimizationTask]
    employees: List[OptimizationEmployee]
    
    # Mappings
    cert_to_idx: Dict[str, int]
    idx_to_cert: Dict[int, str]
    location_to_idx: Dict[str, int]
    
    # Duration Lookup: (original_task_code, aircraft_id, level) -> duration
    # Since OptimizationTask has simplified IDs, we might want map: (task_id, level) -> duration
    # Moved to end to avoid dataclass error
    
    # Matrices (Numpy)
    # distance_matrix[from_loc_idx, to_loc_idx] -> travel_time (int minutes/seconds)
    distance_matrix: np.ndarray 
    
    # Helper to reconstruct solution
    task_map: Dict[int, Tuple[str, str]] = field(default_factory=dict) # id -> (aircraft_id, task_code)

    task_level_durations: Dict[Tuple[int, int], int] = field(default_factory=dict)

@dataclass
class SolutionState:
    """Mutable state of the solution."""
    # assignment[task_id] = employee_id (or -1 if unassigned)
    assignments: Dict[int, int] = field(default_factory=dict)
    
    # start_times[task_id] = start_timestamp
    start_times: Dict[int, int] = field(default_factory=dict)
    
    dropped_tasks: List[int] = field(default_factory=list)
    
    def copy(self) -> 'SolutionState':
        return SolutionState(
            assignments=self.assignments.copy(),
            start_times=self.start_times.copy(),
            dropped_tasks=self.dropped_tasks.copy()
        )
