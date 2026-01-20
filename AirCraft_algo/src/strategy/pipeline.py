"""
Pipeline - Chain multiple optimization strategies sequentially.
"""
import time
from typing import List, Optional, Dict, Any
from src.model.context import Context
from src.model.solution import Solution
from src.strategy.base import IStrategy
from src.strategy.optimization.adapter import OptimizationEngineAdapter


class Pipeline(IStrategy):
    """
    Pipeline strategy that chains multiple strategies sequentially.
    
    Each strategy uses the output of the previous strategy as its initial solution.
    This enables:
    - Warm-starting expensive solvers with greedy heuristics
    - Multi-stage optimization (construct → improve → refine)
    - Hybrid algorithms combining different approaches
    
    Example:
        pipeline = Pipeline([
            GreedyStrategy(),      # Fast construction
            OrStrategy(),          # Optimization with warm-start
            LocalSearchStrategy()  # Fine-tuning
        ])
        solution = pipeline.run(context)
    """
    
    def __init__(self, strategies: List[IStrategy]):
        """
        Initialize pipeline with a list of strategies.
        
        Args:
            strategies: List of strategy instances to execute in order
        """
        super().__init__()
        self.strategies = strategies
        self.intermediate_solutions = []  # Track solutions at each stage
        self.solve_time = 0.0
        self._last_strategy = None
    
    def execute(self) -> Solution:
        """
        Execute all strategies in sequence.
        
        Returns:
            Final solution from the last strategy
        """
        if not self.strategies:
            return Solution.empty()
        
        # Start with initial solution (may be empty or provided)
        current_solution = self.solution
        self.intermediate_solutions = []
        
        start_time = time.time()
        
        # Execute each strategy sequentially
        for idx, strategy in enumerate(self.strategies):
            # Run strategy with current solution as initial
            strategy.init(self.context, current_solution)
            current_solution = strategy.execute()
            
            # Track intermediate result
            self.intermediate_solutions.append(current_solution)
            self._last_strategy = strategy
        
        self.solve_time = time.time() - start_time
        
        return current_solution
    
    def get_intermediate_solutions(self) -> List[Solution]:
        """
        Get solutions from each stage of the pipeline.
        
        Returns:
            List of solutions, one per strategy
        """
        return self.intermediate_solutions
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get solver metadata for output.
        
        Returns:
            Dict with strategy, isOptimal, solveTime
        """
        strategy_name = 'unknown'
        is_optimal = None
        
        if self._last_strategy:
            strategy_name = self._last_strategy.__class__.__name__
            is_optimal = getattr(self._last_strategy, 'is_optimal', None)
        
        return {
            'strategy': strategy_name,
            'isOptimal': is_optimal,
            'solveTime': round(self.solve_time, 2)
        }
    
    def run_with_metadata(self, context: Context, initial_solution: Solution = None) -> tuple:
        """
        Run pipeline and return solution with metadata.
        
        Args:
            context: Input context
            initial_solution: Optional warm-start solution
            
        Returns:
            Tuple of (Solution, metadata_dict)
        """
        self.init(context, initial_solution)
        solution = self.execute()
        metadata = self.get_metadata()
        return solution, metadata
