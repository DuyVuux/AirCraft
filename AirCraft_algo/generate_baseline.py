
import json
import os
import sys

# Add current directory to path to allow imports from src
sys.path.append(os.getcwd())

from src.model.context import Context
from src.strategy.greedyStrategy.greedy_strategy import GreedyStrategy

def run():
    input_path = 'input_complex.json'
    # Ensure the output directory exists
    output_dir = '../deepcode_context/datasets'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'output_baseline.json')
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
        return

    print(f"Loading input from {input_path}...")
    with open(input_path, 'r') as f:
        data = json.load(f)
        
    try:
        context = Context.from_dict(data)
        print("Context loaded successfully.")
    except Exception as e:
        print(f"Error loading context: {e}")
        return
    
    try:
        strategy = GreedyStrategy()
        # IStrategy usually has an init method to set context
        if hasattr(strategy, 'init'):
            strategy.init(context)
        else:
            # Fallback if init doesn't exist, try setting context directly
            strategy.context = context
            
        print("Running Greedy Strategy...")
        solution = strategy.execute()
        
        print(f"Saving solution to {output_path}...")
        with open(output_path, 'w') as f:
            json.dump(solution.to_dict(), f, indent=2)
        print("Done.")
        
    except Exception as e:
        print(f"Error running strategy: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run()
