from typing import List, Dict, Set, Tuple
import numpy as np
from src.model.context import Context
from src.strategy.optimization.models import (
    OptimizationContext, OptimizationTask, OptimizationEmployee
)

class ContextBuilder:
    def build(self, ctx: Context) -> OptimizationContext:
        """
        Convert the High-Level Context (Pydantic models) into the 
        OptimizationContext (Integer-based, flattened, Numpy-ready).
        """
        
        # 1. Flatten Certificates and Create Mapping
        all_certs = set()
        # Collect from Aircraft Requirements
        for ac in ctx.aircrafts:
            for task in ac.requiredTasks:
                all_certs.update(task.requiredCertificates)
        # Collect from Employees
        for emp in ctx.employees:
            all_certs.update(emp.certifications)
            if emp.eType and emp.eType.certificates:
                all_certs.update(emp.eType.certificates)

        sorted_certs = sorted(all_certs)
        cert_to_idx = {c: i for i, c in enumerate(sorted_certs)}
        idx_to_cert = {i: c for i, c in enumerate(sorted_certs)}
        
        # 2. Map Locations (Robust Logic)
        # Collect all locations encountered in the context
        all_locs = set(ctx.matrixConfigs.location_to_idx.keys())
        for ac in ctx.aircrafts:
            if ac.location and ac.location.locationId:
                all_locs.add(ac.location.locationId)
        for emp in ctx.employees:
            if emp.currentLocation:
                all_locs.add(emp.currentLocation)
        
        sorted_locs = sorted(all_locs)
        loc_to_idx = {loc: i for i, loc in enumerate(sorted_locs)}
        
        # Re-build/Expand Distance Matrix
        n_loc = len(sorted_locs)
        # Default travel time 1200s (20 mins) for unknown paths to be conservative but not blocking
        dist_matrix = np.full((n_loc, n_loc), 1200.0) 
        np.fill_diagonal(dist_matrix, 0)
        
        # Copy existing values
        old_map = ctx.matrixConfigs.location_to_idx
        old_matrix = ctx.matrixConfigs.distance_matrix
        if old_matrix is not None:
             for src, old_s_idx in old_map.items():
                 for dest, old_d_idx in old_map.items():
                     if src in loc_to_idx and dest in loc_to_idx:
                         new_s = loc_to_idx[src]
                         new_d = loc_to_idx[dest]
                         val = old_matrix[old_s_idx, old_d_idx]
                         if not np.isinf(val): # Only copy valid paths
                            dist_matrix[new_s, new_d] = val
        
        # 3. Create Time Entry Lookup Map
        # V2: Key includes level for level-based duration
        # Key: (aircraftId, taskCode, level) -> duration (int seconds)
        duration_map = {}
        for te in ctx.matrixConfigs.time_entries:
            key = (te.aircraftId, te.taskCode, te.level)
            duration_map[key] = te.timeProcess
        
        # Also store by (aircraftId, taskCode) for fallback - use median duration
        duration_fallback = {}
        for te in ctx.matrixConfigs.time_entries:
            key = (te.aircraftId, te.taskCode)
            if key not in duration_fallback:
                duration_fallback[key] = []
            duration_fallback[key].append(te.timeProcess)

        # 4. Create OptimizationTasks
        opt_tasks: List[OptimizationTask] = []
        task_level_durations = {}
        task_counter = 0
        task_map = {}
        
        for ac in ctx.aircrafts:
            aircraft_loc_idx = loc_to_idx.get(ac.location.locationId)
            
            if aircraft_loc_idx is None:
                print(f"[WARN] Aircraft {ac.aircraftId} location {ac.location.locationId} not found. Skipping.")
                continue

            for t in ac.requiredTasks:
                req_certs_indices = [
                    cert_to_idx[c] for c in t.requiredCertificates 
                    if c in cert_to_idx
                ]
                
                # V2: Lookup Duration with level
                # Use minLevel as baseline - this is the minimum capable level
                d = None
                for level in [t.minLevel, 2, 1, 3]:
                    d = duration_map.get((ac.aircraftId, t.taskCode, level))
                    if d:
                        break
                    d = duration_map.get(("ANY", t.taskCode, level))
                    if d:
                        break
                
                # Fallback to average of available durations
                if d is None:
                    fallback_key = (ac.aircraftId, t.taskCode)
                    if fallback_key in duration_fallback:
                        d = int(sum(duration_fallback[fallback_key]) / len(duration_fallback[fallback_key]))
                    else:
                        fallback_key = ("ANY", t.taskCode)
                        if fallback_key in duration_fallback:
                            d = int(sum(duration_fallback[fallback_key]) / len(duration_fallback[fallback_key]))
                        else:
                            print(f"[WARN] No time entry for {ac.aircraftId} - {t.taskCode}. Using default 1800s.")
                            d = 1800

                
                # Parse Time Window
                # Aircraft TimeWindow: start/end are ISO strings. 
                # Use src.model.time tools or just parse if possible.
                # But OptimizationTask expects integers (timestamps or relative).
                # Aircraft model has TimeWindow object, assume it parsed dict correctly.
                # But wait, Aircraft.from_dict parses TimeWindow. 
                # TimeWindow.start is ISO string. 
                # We need to convert to int timestamp. 
                # Let's import parse_time from src.model.time if needed, or implement helper.
                
                # Helper for time parsing inside here to avoid circ imports or just simple logic
                from src.model.time import parse_time
                es = parse_time(ac.timeWindow.start)
                lf = parse_time(ac.timeWindow.end)
                
                opt_task = OptimizationTask(
                    id=task_counter,
                    original_task_code=t.taskCode,
                    aircraft_id=ac.aircraftId,
                    earliest_start=es,
                    latest_finish=lf,
                    duration=d,
                    location_idx=aircraft_loc_idx,
                    required_certs=req_certs_indices,
                    min_level=t.minLevel,
                    dependencies=t.dependencies
                )
                
                opt_tasks.append(opt_task)
                task_map[task_counter] = (ac.aircraftId, t.taskCode)
                
                # Populate task_level_durations for levels 1,2,3
                for lvl in [1, 2, 3]:
                    # Try specific
                    dur = duration_map.get((ac.aircraftId, t.taskCode, lvl))
                    if not dur:
                        # Try ANY aircraft
                        dur = duration_map.get(("ANY", t.taskCode, lvl))
                    
                    if not dur:
                        # Fallback to calculated 'd' (nominal) or re-run fallback logic
                        # Simplified: use 'd' if we can't find specific level info
                        # But d was calculated using 'minLevel'.
                        # If data has levels, we assume duration_map works.
                        # If not, use d.
                        dur = d
                    
                    task_level_durations[(task_counter, lvl)] = dur

                task_counter += 1
                
        # 5. Create OptimizationEmployees
        opt_employees: List[OptimizationEmployee] = []
        for i, emp in enumerate(ctx.employees):
            emp_certs = set(emp.certifications)
            if emp.eType:
                emp_certs.update(emp.eType.certificates)
            
            cert_indices = {cert_to_idx[c] for c in emp_certs if c in cert_to_idx}
            
            shifts = []
            from src.model.time import parse_time
            for tw in emp.workingTimes:
                shifts.append((parse_time(tw.start), parse_time(tw.end)))
            
            breaks = []
            for brk in emp.fixedBreakTimes:
                breaks.append((parse_time(brk.start), parse_time(brk.end)))
            
            start_loc_idx = None
            if emp.currentLocation:
                 start_loc_idx = loc_to_idx.get(emp.currentLocation)
            
            emp_level = emp.eType.level if emp.eType else 1
            
            opt_emp = OptimizationEmployee(
                id=i,
                original_id=emp.employeeId,
                certs=cert_indices,
                shifts=shifts,
                start_location_idx=start_loc_idx,
                level=emp_level,
                breaks=breaks
            )
            opt_employees.append(opt_emp)

        # 6. Distance Matrix is already built in Step 2
        pass

        return OptimizationContext(
            tasks=opt_tasks,
            employees=opt_employees,
            cert_to_idx=cert_to_idx,
            idx_to_cert=idx_to_cert,
            location_to_idx=loc_to_idx,
            distance_matrix=dist_matrix,
            task_map=task_map,
            task_level_durations=task_level_durations
        )
