import json
import os

INPUT_FILE = 'data/input/input_complex_v2.json'

def parallelize():
    print(f"Updating dependencies in {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)
        
    count = 0
    for ac in data['aircrafts']:
        tasks = ac.get('requiredTasks', [])
        fuel_task = next((t for t in tasks if t['taskCode'] == 'FUEL'), None)
        
        if fuel_task:
            deps = fuel_task.get('dependencies', [])
            if 'CLEAN' in deps:
                # Remove CLEAN
                deps.remove('CLEAN')
                # Add UNLOAD if not present (to ensure it doesn't start before unload)
                if 'UNLOAD' not in deps:
                    deps.append('UNLOAD')
                
                fuel_task['dependencies'] = deps
                count += 1
                
    print(f"Updated {count} aircraft configurations.")
    
    with open(INPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print("Success! File saved.")

if __name__ == "__main__":
    parallelize()
