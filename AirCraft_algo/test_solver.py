import json
import logging
import sys
from src.model.context import Context
from src.strategy.optimization.adapter import OptimizationEngineAdapter

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

with open('data/input/input_complex_v2.json', 'r') as f:
    data = json.load(f)

ctx = Context.from_dict(data)
strategy = OptimizationEngineAdapter()
strategy.init(ctx)
solution = strategy.execute()

if solution:
    print(f"Optimal: {getattr(strategy, 'is_optimal', False)}")
    assigned = sum(len(emp.assignments) for emp in solution.employees)
    print(f"Assigned tasks: {assigned}")
    print(f"Dropped tasks: {len(solution.droppedTasks)}")
    with open('solution_test.json', 'w') as f:
        json.dump(solution.to_dict(), f, indent=2)
else:
    print("No solution found.")
