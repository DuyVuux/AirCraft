
import sys
import os
import json
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.model.context import Context
from src.strategy.greedyStrategy.greedy_strategy import GreedyStrategy

def test_complex():
    print("Loading Complex Data...")
    with open('input_complex.json', 'r') as f:
        data = json.load(f)
        
    context = Context.from_dict(data)
    print(f"Loaded {len(context.aircrafts)} aircrafts, {len(context.employees)} employees.")
    
    strategy = GreedyStrategy()
    
    start_time = time.time()
    solution = strategy.run(context)
    end_time = time.time()
    
    total_assigned = sum(len(e.assignments) for e in solution.employees)
    total_dropped = sum(len(ac.tasks) for ac in solution.droppedTasks)
    total_tasks = total_assigned + total_dropped
    
    print(f"\n--- Results ---")
    print(f"Time: {end_time - start_time:.4f}s")
    print(f"Total Tasks: {total_tasks}")
    print(f"Assigned: {total_assigned} ({total_assigned/total_tasks*100:.1f}%)")
    print(f"Dropped:  {total_dropped} ({total_dropped/total_tasks*100:.1f}%)")
    
    if total_dropped > 0:
        print(f"\nDropped Details:")
        for ac in solution.droppedTasks:
            print(f"  {ac.aircraftId}: {len(ac.tasks)} tasks")

if __name__ == "__main__":
    test_complex()
