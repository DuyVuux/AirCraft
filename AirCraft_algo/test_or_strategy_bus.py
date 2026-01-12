"""
Test script for OrStrategy with bus constraints and new objective function.
"""
import json
import sys
from src.model.context import Context
from src.strategy.orStrategy.orStrategy import OrStrategy

def main():
    # Load input
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'input_test_cert.json'
    
    print(f"Loading input from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        input_json = json.load(f)
    
    # Parse context
    print("Parsing context...")
    context = Context.from_dict(input_json)
    
    # Create strategy
    print("Creating OrStrategy...")
    strategy = OrStrategy()
    
    # Solve
    print("Solving...")
    print("=" * 80)
    solution = strategy.run(context)
    
    # Print results
    print("\n" + "=" * 80)
    print("SOLUTION SUMMARY")
    print("=" * 80)
    
    # Count assignments
    total_assignments = sum(len(emp.assignments) for emp in solution.employees)
    total_dropped = sum(len(aircraft.tasks) for aircraft in solution.droppedTasks)
    
    print(f"Total assigned tasks: {total_assignments}")
    print(f"Total dropped tasks: {total_dropped}")
    print(f"Total employees used: {len([e for e in solution.employees if e.assignments])}")
    
    if total_dropped > 0:
        print(f"\nDropped tasks:")
        for aircraft in solution.droppedTasks:
            for task in aircraft.tasks:
                print(f"  - {task.taskCode} (Aircraft: {task.aircraftId})")
    
    # Print assignments by employee
    print("\n" + "=" * 80)
    print("TASK ASSIGNMENTS BY EMPLOYEE")
    print("=" * 80)
    for emp_solution in solution.employees:
        if emp_solution.assignments:
            print(f"\nEmployee: {emp_solution.employeeId}")
            print(f"  Certificates: {', '.join(emp_solution.certificates)}")
            print(f"  Tasks:")
            for assignment in emp_solution.assignments:
                print(f"    {assignment.taskCode:20s} | {assignment.aircraftId:12s} | "
                      f"{assignment.startTime} - {assignment.endTime}")
    
    # Save to output
    output_file = 'solution_output.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        solution_dict = solution.to_dict()
        json.dump(solution_dict, f, indent=2)
    
    print(f"\nSolution saved to: {output_file}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
