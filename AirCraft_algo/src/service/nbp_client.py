from src.utils.logger import get_logger
logger = get_logger("src.service.nbp_client")
"""
NBP Client - Registered API service for aircraft maintenance scheduling.
"""
from typing import Dict, Any, List, Optional
from src.service.registry import APIRegistry, BaseAPIHandler
from src.model.context import Context
from src.model.solution import Solution
from src.strategy import Pipeline, IStrategy
from src.strategy.orStrategy import OrStrategy
from src.utils.request_tracker import RequestTracker
from src.validation import validate_solution


@APIRegistry.register('nbp')
class NBPClient(BaseAPIHandler):
    """
    NBP (Network-Based Planning) Client.
    
    Handles aircraft maintenance scheduling using a pipeline of strategies.
    Automatically tracks all requests/responses with tracking IDs.
    """
    
    def __init__(self, strategies: Optional[List[IStrategy]] = None):
        self.context = None
        self.solution = None
        self.tracker = RequestTracker()
        
        # Default pipeline: OR-Tools only
        if strategies is None:
            strategies = [OrStrategy(time_limit_seconds=60)]
        
        self.pipeline = Pipeline(strategies)
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the NBP pipeline.
        
        Args:
            data: Input JSON (must include 'trackingId' field)
        
        Returns:
            Solution dictionary
        """
        tracking_id = data.get('trackingId', 'unknown')
        
        # Step 1: Parse input JSON
        self.context = Context.from_dict(data)
        
        # Step 2: Run optimization pipeline
        self.solution = self.pipeline.run(self.context)
        
        # Step 3: Validate solution constraints
        validate_solution(self.context, self.solution)
        
        # Step 4: Get output with metadata from pipeline
        output_data = self.solution.to_dict()
        output_data.update(self.pipeline.get_metadata())
        
        # Step 5: Save request/response with tracking ID
        tracking_dir = self.tracker.save_request(tracking_id, data, output_data)
        logger.info(f"[Tracking] Saved to: {tracking_dir}/")
        
        # Step 6: Return solution
        return output_data
    
    def get_context(self) -> Context:
        """Get the parsed context."""
        return self.context
    
    def get_solution(self) -> Solution:
        """Get the solution."""
        return self.solution
    
    def get_intermediate_solutions(self) -> List[Solution]:
        """Get intermediate solutions from each pipeline stage."""
        return self.pipeline.get_intermediate_solutions()