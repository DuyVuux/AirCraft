from src.model.solution import Solution
from datetime import datetime
from typing import Dict, List
from collections import defaultdict
from src.utils.logger import get_logger
logger = get_logger("src.utils.output_describer")

def generate_solution_summary(solution: Solution, output_path: str = "solution_summary.md"):
    """Generate a markdown summary of the solution showing task assignments"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # Header
        f.write(f"# Solution Summary\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Overall Statistics
        total_tasks = sum(len(emp.assignments) for emp in solution.employees)
        total_dropped = sum(len(aircraft.tasks) for aircraft in solution.droppedTasks)
        employees_used = len([emp for emp in solution.employees if len(emp.assignments) > 0])
        
        f.write("## Overall Statistics\n\n")
        f.write("| Metric | Count |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Total Employees | {len(solution.employees)} |\n")
        f.write(f"| Active Employees | {employees_used} |\n")
        f.write(f"| Tasks Assigned | {total_tasks} |\n")
        f.write(f"| Tasks Dropped | {total_dropped} |\n")
        if total_tasks + total_dropped > 0:
            success_rate = (total_tasks / (total_tasks + total_dropped)) * 100
            f.write(f"| Success Rate | {success_rate:.1f}% |\n")
        f.write("\n")
        
        # Employee Assignments
        if solution.employees:
            f.write("## Employee Assignments\n\n")
            
            for emp in solution.employees:
                if len(emp.assignments) == 0:
                    continue
                    
                certs = ', '.join(emp.certificates) if emp.certificates else 'None'
                f.write(f"### {emp.employeeId}\n")
                f.write(f"- **Certificates:** {certs}\n\n")
                f.write(f"**Tasks:** {len(emp.assignments)} | **Breaks:** {len(emp.breakTimes)}\n\n")
                
                if emp.assignments:
                    f.write("| # | Task | Aircraft | Location | Start Time | End Time | Duration |\n")
                    f.write("|---|------|----------|----------|------------|----------|----------|\n")
                    
                    for idx, task in enumerate(emp.assignments, 1):
                        duration = "N/A"
                        try:
                            from datetime import datetime as dt
                            start = dt.fromisoformat(task.startTime.replace('Z', '+00:00'))
                            end = dt.fromisoformat(task.endTime.replace('Z', '+00:00'))
                            duration_sec = (end - start).total_seconds()
                            duration = f"{int(duration_sec//60)}m"
                        except:
                            pass
                        
                        f.write(f"| {idx} | `{task.taskCode}` | {task.aircraftId} | {task.locationId} | {task.startTime} | {task.endTime} | {duration} |\n")
                    
                    f.write("\n")
                
                if emp.breakTimes:
                    f.write("**Break Times:**\n")
                    for brk in emp.breakTimes:
                        f.write(f"- {brk.startTime} → {brk.endTime}\n")
                    f.write("\n")
        
        # Aircraft View (Tasks by Aircraft)
        f.write("## Aircraft View\n\n")
        
        # Group tasks by aircraft
        aircraft_tasks: Dict[str, List] = defaultdict(list)
        for emp in solution.employees:
            for task in emp.assignments:
                aircraft_tasks[task.aircraftId].append({
                    'employee': emp.employeeId,
                    'task': task
                })
        
        if aircraft_tasks:
            for aircraft_id, tasks in sorted(aircraft_tasks.items()):
                f.write(f"### {aircraft_id}\n\n")
                f.write(f"**Total Tasks:** {len(tasks)}\n\n")
                
                f.write("| Task | Employee | Start Time | End Time |\n")
                f.write("|------|----------|------------|----------|\n")
                
                # Sort by start time
                tasks_sorted = sorted(tasks, key=lambda x: x['task'].startTime)
                for item in tasks_sorted:
                    task = item['task']
                    f.write(f"| `{task.taskCode}` | {item['employee']} | {task.startTime} | {task.endTime} |\n")
                
                f.write("\n")
        
        # Dropped Tasks
        if solution.droppedTasks:
            f.write("## [!] Dropped Tasks\n\n")
            f.write("> Tasks that could not be assigned due to constraints\n\n")
            
            for aircraft in solution.droppedTasks:
                f.write(f"### {aircraft.aircraftId}\n\n")
                f.write("| Task Code | Required Certificates |\n")
                f.write("|-----------|----------------------|\n")
                
                for task in aircraft.tasks:
                    certs = ', '.join(task.requiredCertificates) if task.requiredCertificates else 'None'
                    f.write(f"| `{task.taskCode}` | {certs} |\n")
                
                f.write("\n")
        else:
            f.write("## [OK] All Tasks Assigned\n\n")
            f.write("No tasks were dropped. All required tasks have been successfully assigned.\n\n")
        
        # Task Type Summary
        f.write("## Task Type Summary\n\n")
        
        task_counts: Dict[str, int] = defaultdict(int)
        for emp in solution.employees:
            for task in emp.assignments:
                task_counts[task.taskCode] += 1
        
        if task_counts:
            f.write("| Task Code | Count |\n")
            f.write("|-----------|-------|\n")
            for task_code, count in sorted(task_counts.items()):
                f.write(f"| `{task_code}` | {count} |\n")
            f.write("\n")
    
    logger.info(f"[OK] Generated solution summary: {output_path}")
