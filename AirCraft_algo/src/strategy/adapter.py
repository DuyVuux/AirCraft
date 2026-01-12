"""
Data Adapter Interface - Generic interface for converting between domain models and algorithm internals.

This interface is shared across multiple optimization strategies (OR-Tools, metaheuristics, etc.)
"""
from abc import ABC, abstractmethod
from typing import Any, Optional
from src.model.context import Context
from src.model.solution import Solution


class IDataAdapter(ABC):
    """
    Interface for data conversion between domain models and algorithm-specific structures.
    
    Each optimization strategy implements this to handle:
    - Parsing Context into internal data structures
    - Converting existing Solutions into algorithm hints/initial states
    - Extracting algorithm results back to Solution model
    """
    
    @abstractmethod
    def parse_context(self, context: Context) -> Any:
        """
        Parse Context into algorithm-specific internal data structure.
        
        Args:
            context: Input context containing aircrafts, employees, matrices
            
        Returns:
            Algorithm-specific data structure (e.g., dict with tasks, employees, matrices)
        """
        pass
    
    @abstractmethod
    def solution_to_hints(self, solution: Solution, context: Context) -> Any:
        """
        Convert an existing Solution into algorithm-specific hints/initial state.
        
        Args:
            solution: Existing solution to use as initial state
            context: Original context for reference
            
        Returns:
            Algorithm-specific hints structure (e.g., variable assignments for OR-Tools)
        """
        pass
    
    @abstractmethod
    def extract_solution(self, internal_result: Any, context: Context) -> Solution:
        """
        Extract algorithm result into Solution model.
        
        Args:
            internal_result: Algorithm-specific result (e.g., solver state, final schedule)
            context: Original context for reference
            
        Returns:
            Solution object with employee assignments and dropped tasks
        """
        pass
