"""
Greedy Client - API endpoint for greedy-based aircraft maintenance scheduling.
"""
from typing import Dict, Any, List, Optional
from src.service.registry import APIRegistry, BaseAPIHandler
from src.model.context import Context
from src.model.solution import Solution
from src.strategy import Pipeline, IStrategy
from src.strategy.greedyStrategy import GreedyStrategy
from src.utils.request_tracker import RequestTracker
from src.validation import validate_solution


@APIRegistry.register('greedy')
class GreedyClient(BaseAPIHandler):
    """
    Greedy scheduling client.
    
    Uses Earliest Deadline First (EDF) heuristic for fast scheduling.
    Suitable for warm-starting more expensive solvers or quick approximations.
    """
    
    def __init__(self, strategies: Optional[List[IStrategy]] = None):
        self.context = None
        self.solution = None
        self.tracker = RequestTracker()
        
        if strategies is None:
            strategies = [GreedyStrategy()]
        
        self.pipeline = Pipeline(strategies)
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the greedy scheduling pipeline.
        
        Args:
            data: Input JSON (must include 'trackingId' field)
        
        Returns:
            Solution dictionary
        """
        tracking_id = data.get('trackingId', 'unknown')
        
        self.context = Context.from_dict(data)
        
        self.solution = self.pipeline.run(self.context)
        
        validate_solution(self.context, self.solution)
        
        output_data = self.solution.to_dict()
        output_data.update(self.pipeline.get_metadata())
        output_data['strategy'] = 'GreedyStrategy'
        
        tracking_dir = self.tracker.save_request(tracking_id, data, output_data)
        print(f"[Tracking] Greedy solution saved to: {tracking_dir}/")
        
        return output_data
    
    def get_context(self) -> Context:
        """Get the parsed context."""
        return self.context
    
    def get_solution(self) -> Solution:
        """Get the solution."""
        return self.solution
