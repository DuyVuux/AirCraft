from flask import Blueprint, render_template, jsonify, current_app
import os
import json

main = Blueprint('main', __name__, template_folder='../templates', static_folder='../static')

def get_data_dir(folder='output'):
    """Get absolute path to data folder (input or output)."""
    controllers_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(controllers_dir, '..', '..', '..'))
    return os.path.join(base_dir, 'data', folder)

@main.route('/')
def index():
    output_dir = get_data_dir('output')
    input_dir = get_data_dir('input')
    
    # Get base data directory for new structure
    controllers_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(controllers_dir, '..', '..', '..'))
    data_dir = os.path.join(base_dir, 'data')
    
    output_files = []
    
    # New structure: list tracking folders with output.json
    if os.path.exists(data_dir):
        for name in os.listdir(data_dir):
            folder_path = os.path.join(data_dir, name)
            output_path = os.path.join(folder_path, 'output.json')
            if os.path.isdir(folder_path) and os.path.exists(output_path):
                # Use trackingId as filename for API compatibility
                output_files.append(f"{name}.json")
    
    # Legacy structure: flat files in data/output
    if os.path.exists(output_dir):
        legacy_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
        output_files.extend(legacy_files)
    
    # Remove duplicates and sort
    output_files = sorted(set(output_files), reverse=True)
    
    input_files = []
    if os.path.exists(input_dir):
        input_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    
    return render_template('index.html', files=output_files, input_files=input_files)

@main.route('/visualize/<filename>')
def visualize(filename):
    return render_template('visualize.html', filename=filename)

@main.route('/api/data/<filename>')
def get_data(filename):
    """Get combined input+output data for visualization.
    
    Supports two data structures:
    1. New: data/{trackingId}/input.json + output.json
    2. Legacy: data/output/{filename}.json + data/input/{input_file}.json
    """
    output_dir = get_data_dir('output')
    input_dir = get_data_dir('input')
    
    # Get base data directory
    controllers_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(controllers_dir, '..', '..', '..'))
    data_dir = os.path.join(base_dir, 'data')
    
    output_data = None
    input_data = None
    
    # Try new structure first: data/{trackingId}/output.json
    # filename might be a trackingId or full path
    tracking_id = filename.replace('.json', '').replace('_output_cpsat', '').replace('_output_hybrid', '')
    
    # Check if it's a timestamped tracking file like "20260104_183904_PLAN-2024-12-05-001.json"
    import re
    timestamp_match = re.match(r'^\d{8}_\d{6}_(.+)\.json$', filename)
    if timestamp_match:
        tracking_id = timestamp_match.group(1)
    
    new_output_path = os.path.join(data_dir, tracking_id, 'output.json')
    new_input_path = os.path.join(data_dir, tracking_id, 'input.json')
    
    try:
        # Try new structure
        if os.path.exists(new_output_path):
            with open(new_output_path, 'r', encoding='utf-8') as f:
                output_data = json.load(f)
            if os.path.exists(new_input_path):
                with open(new_input_path, 'r', encoding='utf-8') as f:
                    input_data = json.load(f)
        else:
            # Fallback to legacy structure
            output_path = os.path.join(output_dir, filename)
            if not os.path.exists(output_path):
                return jsonify({"error": f"Output file not found: {filename}"}), 404
            
            with open(output_path, 'r', encoding='utf-8') as f:
                output_data = json.load(f)
            
            # Try to find matching input file (legacy)
            input_filename = re.sub(r'_output_(cpsat|hybrid)\.json$', '.json', filename)
            input_path = os.path.join(input_dir, input_filename)
            if os.path.exists(input_path):
                with open(input_path, 'r', encoding='utf-8') as f:
                    input_data = json.load(f)
        
        # Combine data for visualization
        result = {
            'solution': output_data.get('solution', []),
            'droppedTasks': output_data.get('droppedTasks', []),
        }
        
        # Add solution metadata
        result['metadata'] = {
            'filename': filename,
            'trackingId': tracking_id,
            'isOptimal': output_data.get('isOptimal', None),
            'solveTime': output_data.get('solveTime', None),
            'strategy': output_data.get('strategy', 'unknown')
        }
        
        # Add context info from input if available
        if input_data:
            result['input'] = input_data
            
            # Extract employee info (working times, breaks)
            employees_info = {}
            for emp in input_data.get('employees', []):
                emp_id = emp.get('employeeId')
                employees_info[emp_id] = {
                    'level': emp.get('eType', {}).get('level', 1),
                    'role': emp.get('eType', {}).get('role', 'UNKNOWN'),
                    'workingTimes': emp.get('workingTimes', []),
                    'fixedBreakTimes': emp.get('fixedBreakTimes', []),
                    'breakDuration': emp.get('breakDuration', 0)
                }
            result['employeesInfo'] = employees_info
            
            # Extract aircraft info (time windows)
            aircrafts_info = {}
            for ac in input_data.get('aircrafts', []):
                ac_id = ac.get('aircraftId')
                aircrafts_info[ac_id] = {
                    'timeWindow': ac.get('timeWindow', {}),
                    'location': ac.get('location', {}).get('locationId', ''),
                    'aType': ac.get('aType', {})
                }
                # Extract task min levels
                tasks_info = {}
                for task in ac.get('requiredTasks', []):
                    tasks_info[task.get('taskCode')] = {
                        'minLevel': task.get('minLevel', 1)
                    }
                aircrafts_info[ac_id]['tasks'] = tasks_info
            result['aircraftsInfo'] = aircrafts_info
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# =============================================================================
# Input Files & Solver Routes
# =============================================================================

@main.route('/api/inputs')
def list_inputs():
    """List available input files."""
    input_dir = get_data_dir('input')
    files = []
    if os.path.exists(input_dir):
        for f in os.listdir(input_dir):
            if f.endswith('.json'):
                filepath = os.path.join(input_dir, f)
                size = os.path.getsize(filepath)
                files.append({
                    'filename': f,
                    'size': size,
                    'size_kb': round(size / 1024, 1)
                })
    return jsonify({'files': files})


@main.route('/api/solve/<filename>', methods=['POST'])
def solve_input(filename):
    """
    Run solver on the specified input file.
    
    Query params:
    - strategy: 'cpsat' or 'hybrid' (default: 'cpsat')
    - time_limit: seconds (default: 30)
    """
    from flask import request
    
    try:
        input_dir = get_data_dir('input')
        output_dir = get_data_dir('output')
        input_path = os.path.join(input_dir, filename)
        
        if not os.path.exists(input_path):
            return jsonify({"error": f"Input file not found: {filename}"}), 404
        
        # Get parameters
        strategy_name = request.args.get('strategy', 'cpsat')
        time_limit = int(request.args.get('time_limit', 30))
        
        # Load input data
        with open(input_path, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
        # Create context from input
        from src.model.context import Context
        context = Context.from_dict(input_data)
        
        # Select strategy
        if strategy_name == 'hybrid':
            from src.strategy.hybridStrategy import HybridStrategy
            strategy = HybridStrategy(time_limit)
        elif strategy_name == 'greedy':
            from src.strategy.greedyStrategy import GreedyStrategy
            strategy = GreedyStrategy()
        else:
            from src.strategy.orStrategy import OrStrategy
            strategy = OrStrategy(time_limit)
        
        # Run solver
        import time
        start_time = time.time()
        strategy.init(context)
        solution = strategy.execute()
        solve_time = time.time() - start_time
        
        # Save output
        if solution:
            output_data = solution.to_dict()
            
            # Add solver metadata to output
            output_data['isOptimal'] = getattr(strategy, 'is_optimal', None)
            output_data['solveTime'] = round(solve_time, 2)
            output_data['strategy'] = strategy_name
            
            output_filename = filename.replace('.json', f'_output_{strategy_name}.json')
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
            
            # Calculate stats
            assigned_count = sum(len(emp.assignments) for emp in solution.employees)
            total_tasks = sum(len(ac.requiredTasks) for ac in context.aircrafts)
            
            return jsonify({
                "success": True,
                "strategy": strategy_name,
                "solve_time_s": round(solve_time, 2),
                "assigned_tasks": assigned_count,
                "total_tasks": total_tasks,
                "output_file": output_filename,
                "message": f"Solution saved to {output_filename}"
            })
        else:
            return jsonify({
                "success": False,
                "error": "No solution found",
                "solve_time_s": round(solve_time, 2)
            }), 400
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@main.route('/api/visualization/<filename>')
def get_visualization_data(filename):
    """Get data for visualization (alias for compatibility)."""
    return get_data(filename)


# =============================================================================
# Benchmark Routes
# =============================================================================

@main.route('/benchmark')
def benchmark_page():
    """Render benchmark dashboard."""
    return render_template('benchmark.html')


@main.route('/api/benchmark/run', methods=['POST'])
def run_benchmark():
    """
    Run benchmark comparison.
    
    Request body:
    {
        "strategies": ["cpsat", "hybrid"],
        "sizes": ["small", "medium"],
        "time_limit": 30,
        "custom_config": {  // optional
            "num_aircrafts": 5,
            "tasks_per_aircraft": 4,
            "num_employees": 10
        }
    }
    
    Returns benchmark results.
    """
    from flask import request
    
    try:
        data = request.get_json() or {}
        strategies = data.get('strategies', ['cpsat', 'hybrid'])
        sizes = data.get('sizes', ['small', 'medium'])
        time_limit = data.get('time_limit', 30)
        custom_config = data.get('custom_config', None)
        
        # Import benchmark runner and generator
        from src.benchmark import BenchmarkRunner
        from src.benchmark.generator import INSTANCE_CONFIGS
        
        # Handle custom configuration - MUST be set before creating runner
        if custom_config:
            INSTANCE_CONFIGS['custom'] = {
                'num_aircrafts': custom_config.get('num_aircrafts', 5),
                'tasks_per_aircraft': custom_config.get('tasks_per_aircraft', 4),
                'num_employees': custom_config.get('num_employees', 10)
            }
            # Make sure 'custom' is in sizes if custom_config is provided
            if 'custom' not in sizes:
                sizes = ['custom']
        
        runner = BenchmarkRunner(time_limit_seconds=time_limit)
        
        results = runner.run_comparison(
            strategies=strategies,
            sizes=sizes,
            num_instances=1
        )
        
        return jsonify(runner.to_dict())
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@main.route('/api/benchmark/strategies')
def get_strategies():
    """Get available benchmark strategies."""
    return jsonify({
        'strategies': [
            {'id': 'cpsat', 'name': 'CP-SAT (OR-Tools)', 'description': 'Standard constraint programming solver'},
            {'id': 'hybrid', 'name': 'Hybrid (CP-SAT + MIP)', 'description': 'Two-phase approach with MIP optimization'}
        ],
        'sizes': [
            {'id': 'small', 'name': 'Small', 'tasks': 9, 'employees': 5},
            {'id': 'medium', 'name': 'Medium', 'tasks': 50, 'employees': 20},
            {'id': 'large', 'name': 'Large', 'tasks': 100, 'employees': 40}
        ]
    })
