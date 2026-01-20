import json
from datetime import datetime, timedelta

INPUT_FILE = 'input_data_2026-01-12.json'
OUTPUT_FILE = 'input_data_2026-01-12.json'

TARGET_DATE = "2026-01-02"

def parse_date(date_str):
    # Try different formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ" 
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
    return None

def main():
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)
        
    print(f"Loaded {len(data['aircrafts'])} aircrafts.")
    
    # Update Aircrafts
    for ac in data['aircrafts']:
        tw = ac['timeWindow']
        start_dt = parse_date(tw['start'])
        end_dt = parse_date(tw['end'])
        
        if not start_dt or not end_dt:
            print(f"Skipping aircraft {ac['aircraftId']}: bad date format")
            continue
            
        # 1. Fix inverted window
        if start_dt > end_dt:
            print(f"Fixing inverted window for {ac['aircraftId']}")
            start_dt, end_dt = end_dt, start_dt
            
        # 2. Shift to Target Date (Keep time)
        # Note: employee working times are around 2026-01-02
        target_dt = datetime.strptime(TARGET_DATE, "%Y-%m-%d")
        
        new_start = start_dt.replace(year=target_dt.year, month=target_dt.month, day=target_dt.day)
        new_end = end_dt.replace(year=target_dt.year, month=target_dt.month, day=target_dt.day)
        
        # If end was next day (e.g. crossing midnight), handle it?
        # For simplicity, let's assume single day ops for now, or respect original duration
        duration = end_dt - start_dt
        new_end = new_start + duration
        
        # Update
        # Use ISO format to match employees for consistency
        ac['timeWindow']['start'] = new_start.isoformat() + "Z"
        ac['timeWindow']['end'] = new_end.isoformat() + "Z"
        
    print("Writing updated data...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print("Done.")

if __name__ == "__main__":
    main()
