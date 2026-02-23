
import sys
import os
import json
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.model.context import Context
from src.strategy.greedyStrategy.greedy_strategy import GreedyStrategy

def analyze():
    print("Running Analysis on input_complex_v2.json...")
    with open('data/input/input_complex_v2.json', 'r') as f:
        data = json.load(f)
    context = Context.from_dict(data)
    
    # Load solution from file
    with open('data/output/input_complex_v2_output_lns.json', 'r') as f:
        sol_data = json.load(f)
        
    # Reconstruct basic solution object for analysis
    # We only need employees assignments and dropped tasks
    from src.model.solution import Solution, EmployeeSolution, DroppedAircraft, DroppedTask, TaskAssignment
    
    solution = Solution.empty()
    dropped_data = sol_data.get('droppedTasks', [])
    
    # Parse dropped tasks
    for item in dropped_data:
        ac_dropped = DroppedAircraft(aircraftId=item['aircraftId'])
        for t in item['tasks']:
            ac_dropped.tasks.append(DroppedTask(
                taskCode=t['taskCode'],
                aircraftId=t['aircraftId'],
                requiredCertificates=t.get('requiredCertificates', []),
                locationId=t.get('locationId'),
                requiredLevel=t.get('requiredLevel')
            ))
        solution.droppedTasks.append(ac_dropped)
        
    # Parse assignments
    for emp_data in sol_data.get('solution', []):
        emp_sol = EmployeeSolution(
            employeeId=emp_data['employeeId'],
            certificates=emp_data.get('certificates', [])
        )
        for assign in emp_data.get('assignment', []):
            # Try to get taskCode, handle both nested task object (legacy) and direct fields
            task_info = assign.get('task', {})
            task_code = task_info.get('taskCode') if isinstance(task_info, dict) else assign.get('taskCode')
            
            emp_sol.assignments.append(TaskAssignment(
                taskCode=task_code,
                aircraftId=task_info.get('aircraftId') if isinstance(task_info, dict) else assign.get('aircraftId'),
                requiredCertificates=[], 
                locationId=assign.get('locationId', ''),
                startTime=assign.get('startTime', ''),
                endTime=assign.get('endTime', '')
            ))
        solution.employees.append(emp_sol)
    
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

    print(f"\n--- Deep Dive Analysis ---")
    
    # 3. Analyze Level Constraints
    print(f"\n[Constraint Check 1: Level Mismatch]")
    
    # Get max level per role from workforce
    max_level_by_role = defaultdict(int)
    count_by_role_level = defaultdict(int)
    
    for emp in context.employees:
        role = emp.eType.role
        level = emp.eType.level
        max_level_by_role[role] = max(max_level_by_role[role], level)
        count_by_role_level[(role, level)] += 1
        
    print("Workforce Capability:")
    for (role, level), count in sorted(count_by_role_level.items()):
        print(f"  {role:<15} Lv.{level}: {count} employees")
        
    print("\nDropped Tasks Requirements:")
    dropped_breakdown = defaultdict(int)
    for ac_drop in solution.droppedTasks:
        for t in ac_drop.tasks:
             # Need to find required level. In dropped task dict it might be there
             # In input_complex_v2, requiredTasks have minLevel
             # We need to lookup the task definition from context if possible, or use what we parsed
             
             # The parsed DroppedTask has requiredLevel if we updated it in adapter
             # But let's look up in context to be sure or if adapter didn't populate it for all
             req_level = t.requiredLevel
             if req_level is None:
                 # fallback to context lookup
                 # Find aircraft type
                 ac = next((a for a in context.aircrafts if a.aircraftId == t.aircraftId), None)
                 if ac:
                     # Find task in requiredTasks
                     task_def = next((x for x in ac.requiredTasks if x.taskCode == t.taskCode), None)
                     if task_def:
                         req_level = task_def.minLevel
            
             dropped_breakdown[(t.taskCode, req_level)] += 1
             
    for (code, level), count in sorted(dropped_breakdown.items()):
        role = role_map.get(code, "UNKNOWN")
        max_lvl = max_level_by_role.get(role, 0)
        status = "OK" if max_lvl >= (level or 1) else "FAIL (No qualified staff)"
        print(f"  {code:<10} Lv.{level}: {count:>2} dropped. Max avail Lv: {max_lvl} -> {status}")

    # 4. Analyze Time Overlaps (Peak Demand)
    print(f"\n[Constraint Check 2: Time Window Overlaps]")
    
    # We want to see how many tasks (assigned + dropped) exist in parallel for each role
    # Create events: (time, type, role)
    # type: +1 for start, -1 for end
    
    events = []
    
    # 4.1 Add Assigned Tasks
    for emp in solution.employees:
        # Get role from context
        orig = next((e for e in context.employees if e.employeeId == emp.employeeId), None)
        if not orig: continue
        role = orig.eType.role
        
        for assign in emp.assignments:
            # Parse ISO time
            # 2026-01-02T18:00:00Z
            try:
                # Simplified timestamp (seconds)
                # Just string compare works for sorting, but we need overlap count
                events.append((assign.startTime, 1, role, "Assigned"))
                events.append((assign.endTime, -1, role, "Assigned"))
            except: pass

    # 4.2 Add Dropped Tasks Windows
    # use start_time/end_time from DroppedTask (which we populated with window)
    for ac_drop in solution.droppedTasks:
        for t in ac_drop.tasks:
            # We need to look up role
            role = role_map.get(t.taskCode, "UNKNOWN")
            if t.startTime and t.endTime:
                events.append((t.startTime, 1, role, "Dropped"))
                events.append((t.endTime, -1, role, "Dropped"))
                
    events.sort()
    
    # Simulate timeline
    current_demand = defaultdict(int)
    max_demand = defaultdict(int)
    problem_roles = set()
    
    for t, change, role, type_ in events:
        current_demand[role] += change
        max_demand[role] = max(max_demand[role], current_demand[role])
        
    print("Peak Concurrent Demand (Assigned + Dropped Windows):")
    for role, peak in sorted(max_demand.items()):
        capacity = utilization_by_role[role]['count']
        status = "OVERLOAD" if peak > capacity else "OK"
        print(f"  {role:<15}: Peak {peak:>2} vs Cap {capacity:>2} -> {status}")

    # 5. Analyze Travel Constraints (Focus on CLEANER)
    print(f"\n[Constraint Check 3: Travel Constraint Check (CLEANER Focus)]")
    
    # Filter dropped CLEAN tasks
    clean_drops = []
    for ac_drop in solution.droppedTasks:
        for t in ac_drop.tasks:
            if "CLEAN" in t.taskCode:
                clean_drops.append(t)
                
    if not clean_drops:
        print("  No CLEAN tasks dropped to analyze.")
    else:
        print(f"  Analyzing {len(clean_drops)} dropped CLEAN tasks...")
        
        # Get Matrix
        matrix = context.matrixConfigs
        
        # Check distances from Hubs (Start Locations)
        print("\n  Travel times from Start Locations (Hubs):")
        # Assuming employees start at 'HUB-01' or similar depending on data
        # Let's check employee start locations
        start_locs = set()
        for emp in context.employees:
            if emp.eType.role == "CLEANER":
                start_locs.add(emp.currentLocation)
        
        for t in clean_drops[:5]: # Sample 5
            loc = t.locationId
            print(f"    To Task at {loc}:")
            for start in start_locs:
                dist = matrix.get_travel_time(start, loc)
                print(f"      From {start}: {dist/60:.1f} mins")

        # Check distances between assignments of Cleaners
        print("\n  Travel times between assigned tasks for Cleaners:")
        
        assigned_cleaners = []
        for emp in solution.employees:
            orig = next((e for e in context.employees if e.employeeId == emp.employeeId), None)
            if orig and orig.eType.role == "CLEANER":
                assigned_cleaners.append(emp)
        
        if not assigned_cleaners:
            print("  No Cleaners assigned any task? (Or mapping failed)")
            
        for emp in assigned_cleaners:
            print(f"    Cleaner {emp.employeeId} assignments:")
            orig = next((e for e in context.employees if e.employeeId == emp.employeeId), None)
            current_loc = orig.currentLocation
            
            for assign in emp.assignments:
                next_loc = assign.locationId
                dist = matrix.get_travel_time(current_loc, next_loc)
                print(f"      {current_loc} -> {next_loc} ({dist/60:.1f}m)")
                current_loc = next_loc

    # 6. Analyze Drops Correlation (Cascading Failures)
    print(f"\n[Constraint Check 4: Cascading Failure Analysis]")
    
    # Group drops by Aircraft
    drops_by_ac = defaultdict(list)
    for ac_drop in solution.droppedTasks:
        for t in ac_drop.tasks:
            drops_by_ac[t.aircraftId].append(t.taskCode)
            
    # Check correlation
    clean_drop_count = 0
    clean_with_unload_drop = 0
    clean_isolated = 0
    
    print("Drops by Aircraft:")
    for ac_id, codes in sorted(drops_by_ac.items()):
        print(f"  {ac_id}: {', '.join(codes)}")
        
        if "CLEAN" in codes:
            clean_drop_count += 1
            if "UNLOAD" in codes:
                clean_with_unload_drop += 1
            else:
                clean_isolated += 1
                
    print("\nCorrelation Summary:")
    print(f"  Total Aircraft with Dropped CLEAN: {clean_drop_count}")
    print(f"  -> With Dropped UNLOAD: {clean_with_unload_drop}")
    print(f"  -> Isolated (UNLOAD assigned but CLEAN dropped): {clean_isolated}")
    
    if clean_isolated > 0:
        print("  WARNING: Found isolated CLEAN drops. Ground Handling shortage might NOT be the only cause.")
        print("  Checking if UNLOAD was assigned very late for these cases...")
        
        # Check isolated cases
        for ac_id, codes in drops_by_ac.items():
            if "CLEAN" in codes and "UNLOAD" not in codes:
                # Find UNLOAD assignment for this aircraft
                unload_assign = None
                for emp in solution.employees:
                    for assign in emp.assignments:
                        if assign.aircraftId == ac_id and "UNLOAD" in assign.taskCode:
                            unload_assign = assign
                            break
                    if unload_assign: break
                
                if unload_assign:
                    print(f"    {ac_id}: UNLOAD finish at {unload_assign.endTime}. CHECK: Does this leave room for CLEAN?")
                else:
                    print(f"    {ac_id}: UNLOAD not found in Dropped OR Assigned? (Data integrity error?)")

if __name__ == "__main__":
    analyze()
