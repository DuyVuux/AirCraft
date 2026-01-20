
import sys
import os
import json
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.model.context import Context
from src.strategy.greedyStrategy.greedy_strategy import GreedyStrategy

def analyze():
    print("Running Analysis on input_complex.json...")
    with open('input_complex.json', 'r') as f:
        data = json.load(f)
    context = Context.from_dict(data)
    strategy = GreedyStrategy()
    solution = strategy.run(context)
    
    # 1. Dropped Task Analysis
    dropped_by_code = defaultdict(int)
    dropped_by_cert = defaultdict(int)
    
    total_dropped = 0
    for ac in solution.droppedTasks:
        for task in ac.tasks:
            total_dropped += 1
            dropped_by_code[task.taskCode] += 1
            
            # Identify required role from context map (heuristic)
            # In complex data generator:
            # ARR-M, DEP-M -> MECHANIC
            # UNLOAD, LOAD -> GROUND_HANDLING
            # CLEAN -> CLEANER
            # FUEL -> FUEL_AGENT
            
    print(f"\n--- Dropped Tasks Breakdown (Total: {total_dropped}) ---")
    for code, count in sorted(dropped_by_code.items(), key=lambda x: -x[1]):
        print(f"  {code:<10}: {count:>2}")
        
    print("\n  -> Implied Resource Shortage:")
    # Heuristic mapping based on generation script
    role_map = {
        "ARR-M": "MECHANIC", "DEP-M": "MECHANIC",
        "UNLOAD": "GROUND_HANDLING", "LOAD": "GROUND_HANDLING",
        "CLEAN": "CLEANER",
        "FUEL": "FUEL_AGENT"
    }
    shortage_by_role = defaultdict(int)
    for code, count in dropped_by_code.items():
        role = role_map.get(code, "UNKNOWN")
        shortage_by_role[role] += count
        
    for role, count in sorted(shortage_by_role.items(), key=lambda x: -x[1]):
        print(f"    {role:<15}: {count} tasks dropped")

    # 2. Employee Utilization
    print(f"\n--- Employee Utilization ---")
    
    # Calculate Total Available Minutes per Role
    # 6 Mechanics * 6 hours = 36 hours
    # But window is 6 hours (360 mins)
    
    utilization_by_role = defaultdict(lambda: {'worked': 0, 'count': 0, 'capacity': 0})
    
    # Init capacity
    for emp in context.employees:
        role = emp.eType.role
        utilization_by_role[role]['count'] += 1
        # Sum all working windows
        total_minutes = 0
        for wt in emp.workingTimes:
            # Simple duration parsing assumption (same day)
            # Or just use pre-calc from assignment duration?
            # Let's use assignment duration / total window duration
            pass
            
    # Sum worked minutes
    for emp in solution.employees:
        # Find original emp role
        orig_emp = next(e for e in context.employees if e.employeeId == emp.employeeId)
        role = orig_emp.eType.role
        
        for assign in emp.assignments:
             # Calculate duration
             # 2026-01-02T18:00:00Z
             # Simple string len check or parse?
             # Task durations are fixed in complex data:
             # ARR-M: 30, UNLOAD: 45, CLEAN: 40, FUEL: 30, LOAD: 45, DEP-M: 30
             pass

    # Actually, simpler: Count assigned vs Total possible
    # We know exact durations from config
    task_durations = {
        "ARR-M": 30, "UNLOAD": 45, "CLEAN": 40, 
        "FUEL": 30, "LOAD": 45, "DEP-M": 30
    }
    
    role_stats = defaultdict(lambda: {'assigned_tasks': 0, 'total_capacity_tasks': 0, 'minutes_worked': 0})
    
    # Capacity in minutes (6 hours = 360 mins per person)
    WINDOW_MINUTES = 360
    
    for emp in context.employees:
        role = emp.eType.role
        role_stats[role]['total_capacity_tasks'] += 0 # meaningful? no
        role_stats[role]['capacity_minutes'] = role_stats[role].get('capacity_minutes', 0) + WINDOW_MINUTES

    assigned_employees_map = {e.employeeId: e for e in solution.employees}
    
    for emp in context.employees:
        role = emp.eType.role
        sol_emp = assigned_employees_map.get(emp.employeeId)
        
        minutes = 0
        if sol_emp:
            for assign in sol_emp.assignments:
                code = assign.taskCode
                dur = task_durations.get(code, 30)
                minutes += dur
                role_stats[role]['assigned_tasks'] += 1
        
        role_stats[role]['minutes_worked'] += minutes

    print(f"{'Role':<16} | {'Staff':<5} | {'Tasks':<5} | {'Worked':<7} | {'Cap':<7} | {'Util %':<6}")
    print("-" * 65)
    
    for role, stats in role_stats.items():
        staff_count = utilization_by_role[role]['count']
        worked = stats['minutes_worked']
        cap = stats['capacity_minutes']
        util = (worked / cap * 100) if cap > 0 else 0
        
        print(f"{role:<16} | {staff_count:<5} | {stats['assigned_tasks']:<5} | {worked:<7} | {cap:<7} | {util:.1f}%")

if __name__ == "__main__":
    analyze()
