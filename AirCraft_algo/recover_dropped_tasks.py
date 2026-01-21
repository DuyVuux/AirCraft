import json
import os
import sys

# Add current directory to path so we can import src
sys.path.append(os.getcwd())

from src.service.nbp_client import NBPClient

INPUT_FILE = 'data/input/input_complex.json'
OUTPUT_FILE = 'data/output/input_complex_output_cpsat.json'

def solve_and_save():
    print(f"Loading input from {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)
        
    print("Running Solver (NBPClient)...")
    client = NBPClient() # Uses OrStrategy (CPSAT) by default
    
    # Process
    result = client.process(data)
    
    # Check dropped tasks
    dropped = result.get('droppedTasks', [])
    print(f"Solver finished. Status: {result.get('status', 'UNKNOWN')}")
    print(f"Dropped Tasks: {len(dropped)}")
    
    if dropped:
        print("Warning: There are still dropped tasks!")
    else:
        print("Success: No dropped tasks.")
        
    # Save output
    print(f"Saving output to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(result, f, indent=2)
    print("Done.")

if __name__ == '__main__':
    solve_and_save()
