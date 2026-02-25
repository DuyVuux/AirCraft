import sys
import traceback
sys.path.append('.')
from src.benchmark.generator import InstanceGenerator
from src.strategy.optimization.adapter import OptimizationEngineAdapter

try:
    print('Generating instance...')
    ctx = InstanceGenerator().generate_context('small', 0)
    print('Running adapter...')
    adapter = OptimizationEngineAdapter()
    adapter.init(ctx)
    sol = adapter.execute()
    print('SUCCESS')
except Exception as e:
    traceback.print_exc()
