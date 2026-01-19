"""
Test Greedy Strategy - Verification tests for greedy scheduling algorithm.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.model.context import Context
from src.strategy.greedyStrategy import GreedyStrategy


def test_strategy_import():
    """Test that GreedyStrategy can be imported and instantiated."""
    print("Testing GreedyStrategy import...")
    strategy = GreedyStrategy()
    print(f"✓ GreedyStrategy instantiated: {strategy}")
    return True


def test_with_sample_input():
    """Test with sample input file."""
    print("\nTesting with sample input...")
    
    sample_file = os.path.join(os.path.dirname(__file__), 'input_sample.json')
    if not os.path.exists(sample_file):
        print(f"  ⚠ Sample file not found: {sample_file}")
        return True
    
    with open(sample_file, 'r') as f:
        data = json.load(f)
    
    print(f"  Loading context from {sample_file}...")
    context = Context.from_dict(data)
    print(f"  ✓ Context loaded: {len(context.aircrafts)} aircrafts, {len(context.employees)} employees")
    
    strategy = GreedyStrategy()
    solution = strategy.run(context)
    
    print(f"  ✓ Solution generated:")
    print(f"    - Employees used: {len(solution.employees)}")
    
    total_tasks = 0
    for emp in solution.employees:
        total_tasks += len(emp.assignments)
    print(f"    - Tasks assigned: {total_tasks}")
    
    dropped_count = 0
    for aircraft in solution.droppedTasks:
        dropped_count += len(aircraft.tasks)
    print(f"    - Tasks dropped: {dropped_count}")
    
    return True


def test_with_def123_data():
    """Test with DEF123 dataset if available."""
    print("\nTesting with DEF123 data...")
    
    data_file = os.path.join(os.path.dirname(__file__), 'input_data_2026-01-12.json')
    if not os.path.exists(data_file):
        print(f"  ⚠ Data file not found: {data_file}")
        return True
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print(f"  Loading context from DEF123 data...")
    context = Context.from_dict(data)
    print(f"  ✓ Context loaded: {len(context.aircrafts)} aircrafts, {len(context.employees)} employees")
    
    strategy = GreedyStrategy()
    
    import time
    start_time = time.time()
    solution = strategy.run(context)
    solve_time = time.time() - start_time
    
    print(f"  ✓ Solution generated in {solve_time:.3f}s:")
    print(f"    - Employees used: {len(solution.employees)}")
    
    total_tasks = 0
    for emp in solution.employees:
        total_tasks += len(emp.assignments)
    print(f"    - Tasks assigned: {total_tasks}")
    
    dropped_count = 0
    for aircraft in solution.droppedTasks:
        dropped_count += len(aircraft.tasks)
    print(f"    - Tasks dropped: {dropped_count}")
    
    output_data = solution.to_dict()
    output_data['strategy'] = 'GreedyStrategy'
    output_data['solveTime'] = round(solve_time, 3)
    
    output_file = 'greedy_solution_output.json'
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    print(f"  ✓ Solution saved to: {output_file}")
    
    return True


if __name__ == '__main__':
    print("=" * 60)
    print("Greedy Strategy Verification")
    print("=" * 60)
    
    try:
        test_strategy_import()
        test_with_sample_input()
        test_with_def123_data()
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
