"""
Strategy Interface - Base class for optimization strategies.
"""
from abc import ABC, abstractmethod
from typing import Optional
from src.model.context import Context
from src.model.solution import Solution


class IStrategy(ABC):
    """
    Abstract base interface for optimization strategies.
    
    Each strategy implements a specific algorithm for solving
    the aircraft maintenance scheduling problem.
    """
    
    def __init__(self):
        self.context: Optional[Context] = None
        self.solution: Optional[Solution] = None
    
    def init(self, context: Context, solution: Optional[Solution] = None) -> None:
        """
        Initialize the strategy with context and optional solution.
        
        Args:
            context: The problem context (input data)
            solution: Optional initial solution (default: empty solution)
        """
        self.context = context
        self.solution = solution if solution is not None else Solution.empty()
    
    @abstractmethod
    def execute(self) -> Solution:
        """
        Execute the strategy algorithm.
        
        Returns:
            The optimized solution
        """
        pass
    
    def run(self, context: Context, solution: Optional[Solution] = None) -> Solution:
        """
        Convenience method to init and execute in one call.
        
        Args:
            context: The problem context
            solution: Optional initial solution
            
        Returns:
            The optimized solution
        """
        self.init(context, solution)
        return self.execute()

