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

api = Blueprint('api', __name__, url_prefix='/api')


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



