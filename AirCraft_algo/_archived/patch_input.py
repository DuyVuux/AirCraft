import json
import os

INPUT_FILE = 'data/input/input_complex_v2.json'

def patch():
    print(f"Patching {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)
        
    matrix_config = data.get('matrixConfigs', {})
    distance_matrix = matrix_config.get('distanceMatrix', [])
    
    # Collect all locations existing in the current matrix
    all_locs = set()
    for entry in distance_matrix:
        all_locs.add(entry['srcCode'])
        all_locs.add(entry['destCode'])
        
    # Identify Hubs and Gates
    hubs = [loc for loc in all_locs if loc.startswith('HUB')]
    if not hubs:
        hubs = ['HUB_01'] # Default if not found in matrix but exists in employees
        
    gates = [loc for loc in all_locs if loc.startswith('GATE')]
    
    print(f"Found Hubs: {hubs}")
    print(f"Found Gates: {gates}")
    
    # Generate missing entries
    new_entries = []
    
    for hub in hubs:
        for gate in gates:
            # Check if exists (Forward)
            if not any(d['srcCode'] == hub and d['destCode'] == gate for d in distance_matrix):
                new_entries.append({
                    "srcCode": hub,
                    "destCode": gate,
                    "travelTime": 600 # 10 minutes
                })
                
            # Check if exists (Backward)
            if not any(d['srcCode'] == gate and d['destCode'] == hub for d in distance_matrix):
                new_entries.append({
                    "srcCode": gate,
                    "destCode": hub,
                    "travelTime": 600 # 10 minutes
                })
                
    if new_entries:
        print(f"Adding {len(new_entries)} missing entries...")
        distance_matrix.extend(new_entries)
        
        # Save back
        with open(INPUT_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print("Success! File updated.")
    else:
        print("No missing entries found.")

if __name__ == "__main__":
    patch()
