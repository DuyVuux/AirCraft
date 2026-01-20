"""
API Routes - Dynamic endpoint routing using APIRegistry.
"""
import traceback
from flask import Blueprint, jsonify, request
from src.service.registry import get_api_handler
from src.model.context import Context
from src.model.solution import Solution
from src.utils.input_describer import generate_input_description
from src.utils.output_describer import generate_solution_summary
import os
# Import NBPClient to trigger @APIRegistry.register decorator
import src.service.nbp_client  # noqa: F401
import src.service.greedy_client  # noqa: F401
from src.model.time import parse_time

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/scheduler/run', methods=['POST'])
def run_scheduler():
    """
    Endpoint compatible with Frontend 'schedulerApi.ts'.
    Path: POST /api/scheduler/run
    Body: keys: aircrafts, employees, matrixConfigs, config: { algorithm: '...' }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload"}), 400
            
        # 1. Extract Configuration
        config = data.get('config', {})
        algorithm = config.get('algorithm', 'cpsat').lower() # e.g. 'lns', 'greedy', 'ortools'
        
        # 2. Select Handler based on algorithm
        # Map frontend algo names to backend strategies
        if algorithm == 'lns':
             strategy = OptimizationEngineAdapter()
        elif algorithm == 'greedy':
             strategy = GreedyStrategy()
        else:
             # Default to OR-Tools/CP-SAT
             time_limit = int(config.get('timeLimit', 30))
             strategy = OrStrategy(time_limit)
             
        # 3. Build Context
        # Frontend sends data matching Context structure mostly
        # We might need to handle 'trackingId' generation if missing
        if 'trackingId' not in data:
            data['trackingId'] = f"REQ-{int(time.time())}"
            
        ctx = Context.from_dict(data)
        
        # 4. Execute
        strategy.init(ctx)
        solution = strategy.execute()
        
        # 5. Map Solution to Frontend Response (ScheduleResult)
        # Frontend expects: { status, message, scheduledTasks: [], ... }
        
        scheduled_tasks = []
        if solution:
            for emp in solution.employees:
                for assign in emp.assignments:
                    # Resolve duration (approx)
                    duration_min = (parse_time(assign.endTime) - parse_time(assign.startTime)) // 60
                    
                    scheduled_tasks.append({
                        "taskId": f"{assign.taskCode}-{assign.aircraftId}", # Unique key
                        "taskCode": assign.taskCode,
                        "aircraftId": assign.aircraftId,
                        "employeeId": emp.employeeId,
                        "employeeName": f"Emp {emp.employeeId}", # Placeholder if name missing
                        "startTime": assign.startTime,
                        "endTime": assign.endTime,
                        "duration": duration_min
                    })
                    
            return jsonify({
                "status": "OPTIMAL" if not solution.droppedTasks else "FEASIBLE",
                "message": f"Solved using {algorithm.upper()}. Dropped: {len(solution.droppedTasks)} tasks.",
                "scheduledTasks": scheduled_tasks,
                "totalCost": 0, # Placeholder
                "solveTimeMs": 0 # Placeholder
            })
        else:
            return jsonify({
                "status": "FAILED",
                "message": "No solution found",
                "scheduledTasks": [],
                "totalCost": 0,
                "solveTimeMs": 0
            }), 200 # Return 200 with FAILED status so frontend handles gracefuly

    except Exception as e:
        print("\n[ERROR] Scheduler Run Failed:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@api.route('/solver/<api_name>', methods=['POST'])
def handle_api(api_name: str):
    """
    Dynamic API handler using registry pattern.
    
    POST /api/{api_name}
    Body: Input JSON
    
    Currently registered APIs:
    - NBP: Aircraft maintenance scheduling
    """
    try:
        # Get handler from registry
        try:
            handler = get_api_handler(api_name)
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        
        # Get input data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Generate input description (generic for all APIs)
        try:
            tracking_id = data.get('trackingId', 'unknown')
            ctx = Context.from_dict(data)
            
            tracking_dir = os.path.join('data', tracking_id)
            os.makedirs(tracking_dir, exist_ok=True)
            desc_file = os.path.join(tracking_dir, 'input_description.md')
            generate_input_description(ctx, desc_file)
        except Exception as e:
            # Don't fail the request if description generation fails
            print(f"[Warning] Failed to generate input description: {e}")
        
        # Process and return result
        result = handler.process(data)
        
        # Generate solution summary (generic for all APIs)
        try:
            # Parse solution from result dictionary
            solution_data = result.get('solution', [])
            dropped_data = result.get('droppedTasks', [])
            
            # Reconstruct Solution object from dict for summary generation
            from src.model.solution import Solution, EmployeeSolution, TaskAssignment, TimeSlot, DroppedAircraft, DroppedTask
            
            solution = Solution()
            
            # Reconstruct employees
            for emp_data in solution_data:
                emp = solution.add_employee(emp_data['employeeId'], emp_data.get('certificates', []))
                
                # Add assignments
                for assign_data in emp_data.get('assignment', []):
                    task_info = assign_data['task']
                    emp.assignments.append(TaskAssignment(
                        taskCode=task_info['taskCode'],
                        aircraftId=task_info['aircraftId'],
                        requiredCertificates=task_info.get('requiredCertificates', []),
                        locationId=assign_data['locationId'],
                        startTime=assign_data['startTime'],
                        endTime=assign_data['endTime']
                    ))
                
                # Add breaks
                for break_data in emp_data.get('breakTimes', []):
                    emp.breakTimes.append(TimeSlot(
                        startTime=break_data['startTime'],
                        endTime=break_data['endTime']
                    ))
            
            # Reconstruct dropped tasks
            for aircraft_data in dropped_data:
                aircraft = DroppedAircraft(aircraftId=aircraft_data['aircraftId'])
                for task_data in aircraft_data['tasks']:
                    aircraft.tasks.append(DroppedTask(
                        taskCode=task_data['taskCode'],
                        aircraftId=task_data['aircraftId'],
                        requiredCertificates=task_data.get('requiredCertificates', [])
                    ))
                solution.droppedTasks.append(aircraft)
            
            # Generate summary in same tracking directory
            summary_file = os.path.join(tracking_dir, 'output_summary.md')
            generate_solution_summary(solution, summary_file)
            
        except Exception as e:
            # Don't fail the request if summary generation fails
            print(f"[Warning] Failed to generate solution summary: {e}")
        
        return jsonify(result), 200
        
    except Exception as e:
        # Print full traceback for debugging
        print("\n[ERROR] API request failed:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



