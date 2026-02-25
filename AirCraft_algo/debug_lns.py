import sys
sys.path.append('.')
from src.benchmark.generator import InstanceGenerator
from src.strategy.optimization.adapter import OptimizationEngineAdapter

print("Generating small instance...")
ctx = InstanceGenerator.generate_small_instance()
print("Initialized context. Running LNS adapter...")
adapter = OptimizationEngineAdapter()
try:
    adapter.init(ctx)
    sol = adapter.execute()
    print("FINISHED. Assigned:", sum(len(e.assignments) for e in sol.employees))
except Exception as e:
    import traceback
    traceback.print_exc()
