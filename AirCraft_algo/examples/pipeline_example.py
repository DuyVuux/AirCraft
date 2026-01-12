"""
Example: Multi-stage Pipeline
Demonstrates how to use Pipeline with multiple strategies.
"""
from src.strategy import Pipeline
from src.strategy.orStrategy import OrStrategy
from src.model.context import Context

# Example 1: Single-stage (equivalent to direct OrStrategy)
simple_pipeline = Pipeline([
    OrStrategy(time_limit_seconds=60)
])

# Example 2: Multi-stage optimization
# (Future: add GreedyStrategy, LocalSearchStrategy)
multi_stage_pipeline = Pipeline([
    # GreedyStrategy(),              # Fast construction (to be implemented)
    OrStrategy(time_limit_seconds=30),  # Quick optimization
    OrStrategy(time_limit_seconds=60),  # Refinement with warm-start
])

# Example 3: Using in NBPClient
from src.service.nbp_client import NBPClient

# Default: single OR-Tools
client_default = NBPClient()

# Custom pipeline
client_custom = NBPClient(strategies=[
    OrStrategy(time_limit_seconds=30),
    OrStrategy(time_limit_seconds=60)
])

# Usage
context = Context.from_dict(input_data)
solution = client_custom.process(input_data)

# Access intermediate solutions
intermediate = client_custom.pipeline.get_intermediate_solutions()
print(f"After stage 1: {len(intermediate[0].employees)} employees")
print(f"After stage 2: {len(intermediate[1].employees)} employees")
