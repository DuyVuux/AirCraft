import json
from datetime import datetime

INPUT_FILE = 'data/input/input_complex_v2.json'

def parse_time(ts):
    # 2026-01-02T18:07:00Z
    return datetime.strptime(ts.replace('Z', '+0000'), "%Y-%m-%dT%H:%M:%S%z")

def verify():
    print(f"Verifying Chains in {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)
        
    # Build Duration Map
    # matrixConfigs -> timeMatrix
    durations = {} # (code, aircraft, level) -> time. simplified: code -> time (assuming base level)
    
    # In V2, maybe timeMatrix has entry per taskCode only?
    # Let's check typical values
    tm = data['matrixConfigs']['timeMatrix']
    # Aggregated map: code -> min_duration seen
    min_durs = {}
    for entry in tm:
        code = entry['taskCode']
        t = entry['timeProcess']
        if code not in min_durs or t < min_durs[code]:
            min_durs[code] = t
            
    print("Detected Task Durations (Min):")
    for k, v in min_durs.items():
        print(f"  {k}: {v/60:.1f} min")
        
    # Analyze Aircraft
    impossible_count = 0
    total_shortage = 0
    
    for ac in data['aircrafts']:
        aid = ac['aircraftId']
        start = parse_time(ac['timeWindow']['start'])
        end = parse_time(ac['timeWindow']['end'])
        available_seconds = (end - start).total_seconds()
        
        # Build Dependency Graph for this AC
        tasks = {t['taskCode']: t for t in ac['requiredTasks']}
        
        # Calculate Critical Path (Longest Path) using simple recursion with memoization
        memo = {}
        
        def get_path_len(code):
            if code in memo: return memo[code]
            t_def = tasks.get(code)
            if not t_def: return 0
            
            # Own duration
            # Prefer specific entry if possible (omitted for simplicity, using min_avg)
            dur = min_durs.get(code, 1800) # Default 30m
            
            # Max of precursors
            max_prev = 0
            for pred in t_def.get('dependencies', []):
                max_prev = max(max_prev, get_path_len(pred))
                
            total = max_prev + dur
            memo[code] = total
            return total
            
        # Find max path ending at any task (since we don't know the 'sink', check all)
        # Actually usually DEP-M is the sink.
        max_chain = 0
        for code in tasks:
            max_chain = max(max_chain, get_path_len(code))
            
        if max_chain > available_seconds:
            impossible_count += 1
            shortage = (max_chain - available_seconds) / 60
            total_shortage += shortage
            print(f"  {aid}: Req {max_chain/60:.1f}m > Avail {available_seconds/60:.1f}m. Shortage: {shortage:.1f}m")
            
    print(f"\nSummary:")
    print(f"  Total Impossible Aircraft: {impossible_count} / {len(data['aircrafts'])}")
    print(f"  Average Shortage: {total_shortage/max(1, impossible_count):.1f} mins")

if __name__ == "__main__":
    verify()
