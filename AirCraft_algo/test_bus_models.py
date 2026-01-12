import json
from src.model.context import Context

def test_bus_parsing():
    """Test that input_sample.json parses correctly with bus data"""
    
    print("Loading input_sample.json...")
    with open('input_sample.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Parsing with Context.from_dict()...")
    ctx = Context.from_dict(data)
    
    print("\n✅ Parsing successful!\n")
    
    print(f"📊 Summary:")
    print(f"  Aircrafts: {len(ctx.aircrafts)}")
    print(f"  Hubs: {len(ctx.hubs)}")
    print(f"  Employees: {len(ctx.employees)}")
    print(f"  Bus Stops: {len(ctx.busStops)}")
    print(f"  Bus Routes: {len(ctx.busRoutes)}")
    
    print(f"\n🚌 Bus Stops:")
    for bs in ctx.busStops:
        print(f"  - {bs.busStopId}: {bs.bType.desc}")
    
    print(f"\n🚌 Bus Routes:")
    for route in ctx.busRoutes:
        print(f"  - {route.routeId} ({route.routeName})")
        print(f"    Stops: {len(route.stops)}, Cycle: {route.cycleTime}s, Freq: {route.frequency}s")
    
    print(f"\n📐 Matrices:")
    print(f"  Distance matrix: {ctx.matrixConfigs.distance_matrix.shape if ctx.matrixConfigs.distance_matrix is not None else 'None'}")
    print(f"  Time matrix: {ctx.matrixConfigs.time_matrix.shape if ctx.matrixConfigs.time_matrix is not None else 'None'}")
    print(f"  Bus transit matrix: {ctx.matrixConfigs.bus_transit_matrix.shape if ctx.matrixConfigs.bus_transit_matrix is not None else 'None'}")
    print(f"  Bus wait matrix: {ctx.matrixConfigs.bus_wait_matrix.shape if ctx.matrixConfigs.bus_wait_matrix is not None else 'None'}")
    print(f"  Walk to bus matrix: {ctx.matrixConfigs.walk_to_bus_matrix.shape if ctx.matrixConfigs.walk_to_bus_matrix is not None else 'None'}")
    
    # Test helper methods
    print(f"\n🧪 Testing helper methods:")
    transit, wait = ctx.matrixConfigs.get_bus_transit_time('BS_TERMINAL', 'BS_HANGAR')
    print(f"  Bus transit BS_TERMINAL → BS_HANGAR: {transit}s transit, {wait}s wait")
    
    walk = ctx.matrixConfigs.get_walk_to_bus_time('GATE-01', 'BS_TERMINAL')
    print(f"  Walk GATE-01 → BS_TERMINAL: {walk}s")
    
    print("\n✅ All tests passed!")

if __name__ == '__main__':
    test_bus_parsing()
