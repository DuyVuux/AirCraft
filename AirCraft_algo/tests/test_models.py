import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model.context import Context

def test_load_models():
    input_file = 'input_sample.json'
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    try:
        context = Context.from_dict(data)
        print("Successfully parsed Context object.")
        
        # Verify key fields
        print(f"Tracking ID: {context.trackingId}")
        print(f"Number of Aircrafts: {len(context.aircrafts)}")
        print(f"Number of Hubs: {len(context.hubs)}")
        print(f"Number of Employees: {len(context.employees)}")
        
        # Verify specific data point
        first_aircraft = context.aircrafts[0]
        print(f"First Aircraft ID: {first_aircraft.aircraftId}")
        print(f"First Aircraft Type: {first_aircraft.aType.desc}")
        
        first_employee = context.employees[0]
        print(f"First Employee ID: {first_employee.employeeId}")
        print(f"First Employee Role: {first_employee.eType.role}")
        
        print("Data model verification passed.")
        
    except Exception as e:
        print(f"Error parsing data model: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_load_models()
