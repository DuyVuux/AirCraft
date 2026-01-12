from src.model.context import Context
from datetime import datetime
from typing import Optional

def generate_input_description(ctx: Context, output_path: str = "input_description.md"):
    """Generate a markdown file describing the input data structure"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # Header
        f.write(f"# Input Data Description\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Tracking ID:** `{ctx.trackingId}`\n\n")
        f.write("---\n\n")
        
        # Summary table
        f.write("## Summary\n\n")
        f.write("| Entity | Count |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Aircrafts | {len(ctx.aircrafts)} |\n")
        f.write(f"| Hubs | {len(ctx.hubs)} |\n")
        f.write(f"| Employees | {len(ctx.employees)} |\n")
        f.write(f"| Bus Stops | {len(ctx.busStops)} |\n")
        f.write(f"| Bus Routes | {len(ctx.busRoutes)} |\n")
        f.write("\n")
        
        # Aircrafts
        if ctx.aircrafts:
            f.write("## Aircrafts\n\n")
            for ac in ctx.aircrafts:
                f.write(f"### {ac.aircraftId}\n")
                f.write(f"- **Type:** {ac.aType.desc} (`{ac.aType.id}`)\n")
                f.write(f"- **Location:** {ac.location.locationId or 'N/A'} ({ac.location.locationType or 'N/A'})\n")
                f.write(f"  - Coordinates: ({ac.location.longitude}, {ac.location.latitude})\n")
                f.write(f"- **Time Window:** {ac.timeWindow.start} → {ac.timeWindow.end}\n")
                f.write(f"- **Required Tasks:** {len(ac.requiredTasks)}\n")
                for task in ac.requiredTasks:
                    certs = ', '.join(task.requiredCertificates) if task.requiredCertificates else 'None'
                    f.write(f"  - `{task.taskCode}` (required certs: {certs})\n")
                f.write("\n")
        
        # Hubs
        if ctx.hubs:
            f.write("## Hubs\n\n")
            for hub in ctx.hubs:
                f.write(f"### {hub.hubId}\n")
                f.write(f"- **Location:** {hub.location.locationId or 'N/A'} ({hub.location.locationType or 'N/A'})\n")
                f.write(f"  - Coordinates: ({hub.location.longitude}, {hub.location.latitude})\n")
                f.write("\n")
        
        # Employees
        if ctx.employees:
            f.write("## Employees\n\n")
            role_groups = {}
            for emp in ctx.employees:
                role = emp.eType.role
                if role not in role_groups:
                    role_groups[role] = []
                role_groups[role].append(emp)
            
            for role, emps in role_groups.items():
                f.write(f"### {role}\n\n")
                for emp in emps:
                    f.write(f"**{emp.employeeId}**\n")
                    f.write(f"- Certificates: {', '.join(emp.eType.certificates) if emp.eType.certificates else 'None'}\n")
                    if emp.currentLocation:
                        f.write(f"- Current Location: `{emp.currentLocation}`\n")
                    else:
                        f.write(f"- Current Location: Not specified\n")
                    f.write(f"- Working Times: {len(emp.workingTimes)} shift(s)\n")
                    for wt in emp.workingTimes:
                        f.write(f"  - {wt.start} → {wt.end}\n")
                    f.write(f"- Break Duration: {emp.breakDuration}s ({emp.breakDuration//60} min)\n")
                    if emp.fixedBreakTimes:
                        f.write(f"- Fixed Break Times:\n")
                        for bt in emp.fixedBreakTimes:
                            f.write(f"  - {bt.start} → {bt.end}\n")
                    f.write("\n")
        
        # Bus Stops
        if ctx.busStops:
            f.write("## Bus Stops\n\n")
            for bs in ctx.busStops:
                f.write(f"### {bs.busStopId}\n")
                f.write(f"- **Type:** {bs.bType.desc} (`{bs.bType.id}`)\n")
                f.write(f"- **Coordinates:** ({bs.location.longitude}, {bs.location.latitude})\n")
                f.write("\n")
        
        # Bus Routes
        if ctx.busRoutes:
            f.write("## Bus Routes\n\n")
            for route in ctx.busRoutes:
                f.write(f"### {route.routeId} - {route.routeName}\n")
                f.write(f"- **Cycle Time:** {route.cycleTime}s ({route.cycleTime//60} min)\n")
                f.write(f"- **Frequency:** {route.frequency}s ({route.frequency//60} min between departures)\n")
                f.write(f"- **Operating Hours:** {route.operatingHours.start} → {route.operatingHours.end}\n")
                f.write(f"- **Stops:** {len(route.stops)}\n\n")
                
                f.write("| Stop | Arrival | Departure | Duration |\n")
                f.write("|------|---------|-----------|----------|\n")
                for stop in route.stops:
                    arr_min = stop.arrivalTime // 60
                    dep_str = f"{stop.departureTime//60} min" if stop.departureTime else "Terminal"
                    dur_str = f"{stop.stopDuration}s"
                    f.write(f"| {stop.busStopId} | {arr_min} min | {dep_str} | {dur_str} |\n")
                f.write("\n")
        
        # Matrices
        f.write("## Matrices\n\n")
        
        mc = ctx.matrixConfigs
        
        f.write(f"### Distance Matrix\n")
        if mc.distance_matrix is not None:
            f.write(f"- Shape: {mc.distance_matrix.shape}\n")
            f.write(f"- Locations: {len(mc.location_to_idx)}\n")
            f.write(f"- Entries: {len(mc.distance_entries)}\n")
        else:
            f.write("- Not available\n")
        f.write("\n")
        
        f.write(f"### Time Matrix\n")
        if mc.time_matrix is not None:
            f.write(f"- Shape: {mc.time_matrix.shape}\n")
            f.write(f"- Tasks: {len(mc.task_to_idx)}\n")
            f.write(f"- Entries: {len(mc.time_entries)}\n")
        else:
            f.write("- Not available\n")
        f.write("\n")
        
        if mc.bus_transit_matrix is not None:
            f.write(f"### Bus Transit Matrix\n")
            f.write(f"- Shape: {mc.bus_transit_matrix.shape}\n")
            f.write(f"- Bus Stops: {len(mc.bus_stop_to_idx)}\n")
            f.write(f"- Entries: {len(mc.bus_transit_entries)}\n\n")
            
            f.write(f"### Walking Distance to Bus Stops\n")
            if mc.walk_to_bus_matrix is not None:
                f.write(f"- Shape: {mc.walk_to_bus_matrix.shape}\n")
                f.write(f"- Entries: {len(mc.walking_distance_entries)}\n")
            f.write("\n")
    
    print(f"[OK] Generated input description: {output_path}")
