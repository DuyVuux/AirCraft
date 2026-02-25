import json

with open('data/input/input_complex_v2.json', 'r') as f:
    input_data = json.load(f)

for emp in input_data['employees']:
    if emp['employeeId'] in ['EMP_GROUND_HANDLING_1', 'EMP_GROUND_HANDLING_6', 'EMP_GROUND_HANDLING_8']:
         print(f"{emp['employeeId']}:")
         print(f"  Role: {emp['eType']['role']}, Level: {emp['eType']['level']}")
         print(f"  Certs: {emp['eType']['certificates']}")
         print(f"  WorkingTimes: {emp['workingTimes']}")
         print(f"  Breaks: {emp['fixedBreakTimes']}")

