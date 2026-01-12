"""
Data Adapter Interface - Convert between domain models and algorithm internals.

Simple input/output adapter for all optimization algorithms.
"""
from abc import ABC, abstractmethod
from typing import Any
from src.model.context import Context
from src.model.solution import Solution


class IDataAdapter(ABC):
    """
    Generic data adapter interface for optimization algorithms.
    
    Supports any algorithm type:
    - Exact solvers (OR-Tools, MIP)
    - Metaheuristics (GA, SA, Tabu Search)  
    - Heuristics (Greedy, Construction)
    
    Two simple responsibilities:
    1. Input: Convert Context → Algorithm's data structure
    2. Output: Convert Algorithm's result → Solution
    """
    
    @abstractmethod
    def adapt_input(self, context: Context) -> Any:
        """
        Convert Context to algorithm-specific data structure.
        
        Args:
            context: Domain model with aircrafts, employees, time windows, matrices
            
        Returns:
            Internal data structure for the algorithm. Examples:
            - OR-Tools: Dict[tasks, employees, travel_times, durations, ...]
            - GA: Dict[tasks, employees, encoding_map]
            - Greedy: Dict[sorted_tasks, employee_availability]
        """
        pass
    
    @abstractmethod
    def adapt_output(self, internal_result: Any, context: Context) -> Solution:
        """
        Convert algorithm result to Solution model.
        
        Args:
            internal_result: Algorithm's output (solver state, final schedule, etc.)
            context: Original Context for reference/mapping
            
        Returns:
            Domain Solution with employee assignments and dropped tasks
        """
        pass

