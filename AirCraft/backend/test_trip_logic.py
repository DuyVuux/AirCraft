import sys
import os
import numpy as np
from unittest.mock import MagicMock

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mock graph_service and floyd_warshall BEFORE importing trip_generator
# This prevents ModuleNotFoundError for numba if it's not installed
sys.modules['app.services.graph_service'] = MagicMock()
sys.modules['app.services.floyd_warshall'] = MagicMock()
sys.modules['numba'] = MagicMock()

# Now import trip_generator
# It will import the mocks, which is fine because we will replace the functions anyway
import app.services.trip_generator as tg

# Mocking compute_all_shortest_paths and get_shortest_path_info

def mock_compute_all_shortest_paths(nodes, edges):
    n = len(nodes)
    node_to_idx = {node['id']: i for i, node in enumerate(nodes)}
    idx_to_node = {i: node['id'] for i, node in enumerate(nodes)}
    
    dist_matrix = np.full((n, n), np.inf)
    next_matrix = np.full((n, n), -1)
    
    for i in range(n):
        dist_matrix[i, i] = 0
        
    for edge in edges:
        u = node_to_idx[edge['nodeA']]
        v = node_to_idx[edge['nodeB']]
        d = edge['distance']
        dist_matrix[u, v] = d
        if not edge.get('directed', False):
            dist_matrix[v, u] = d
            
    return dist_matrix, next_matrix, node_to_idx, idx_to_node

def mock_get_shortest_path_info(i, j, dist_matrix, next_matrix, idx_to_node, edges):
    dist = dist_matrix[i, j]
    return dist, [], [] # Path doesn't matter for this test

# Replace the imported functions with our mocks
tg.compute_all_shortest_paths = mock_compute_all_shortest_paths
tg.get_shortest_path_info = mock_get_shortest_path_info

def run_test():
    nodes = [
        {'id': 'S1', 'type': 'aircraft_stand', 'name': 'Stand 1'},
        {'id': 'S2', 'type': 'aircraft_stand', 'name': 'Stand 2'},
        {'id': 'S3', 'type': 'aircraft_stand', 'name': 'Stand 3'},
        {'id': 'B1', 'type': 'bus_stop', 'name': 'Bus 1'},
        {'id': 'R1', 'type': 'rest_area', 'name': 'Rest 1'},
    ]
    
    edges = [
        # S1 <-> S2: 30m (Close)
        {'id': 'e1', 'nodeA': 'S1', 'nodeB': 'S2', 'distance': 30.0, 'directed': False},
        # S1 <-> S3: 100m (Far)
        {'id': 'e2', 'nodeA': 'S1', 'nodeB': 'S3', 'distance': 100.0, 'directed': False},
        # B1 -> S1: 200m
        {'id': 'e3', 'nodeA': 'B1', 'nodeB': 'S1', 'distance': 200.0, 'directed': True},
        # R1 -> B1: 10m
        {'id': 'e4', 'nodeA': 'R1', 'nodeB': 'B1', 'distance': 10.0, 'directed': True},
        # R1 -> S1: 40m (Close)
        {'id': 'e5', 'nodeA': 'R1', 'nodeB': 'S1', 'distance': 40.0, 'directed': True},
        # R1 -> S3: 60m (Far)
        {'id': 'e6', 'nodeA': 'R1', 'nodeB': 'S3', 'distance': 60.0, 'directed': True},
    ]
    
    print("Running generate_trips with epsilon_walk=50.0")
    trips = tg.generate_trips(nodes, edges, epsilon_walk=50.0)
    
    print(f"Generated {len(trips)} trips")
    
    # Helper to find trip
    def find_trip(from_id, to_id):
        for t in trips:
            if t['id'] == f"trip_{from_id}_to_{to_id}":
                return t
        return None

    # 1. Stand <-> Stand (Close) -> WALK
    t_s1_s2 = find_trip('S1', 'S2')
    print(f"S1->S2 (30m): {t_s1_s2['mode'] if t_s1_s2 else 'None'} (Expected WALK)")
    assert t_s1_s2['mode'] == 'WALK'
    assert 'proximity_walk' in t_s1_s2['tags']
    assert 'stand_transfer' in t_s1_s2['tags']

    # 2. Stand <-> Stand (Far) -> BUS
    t_s1_s3 = find_trip('S1', 'S3')
    print(f"S1->S3 (100m): {t_s1_s3['mode'] if t_s1_s3 else 'None'} (Expected BUS)")
    assert t_s1_s3['mode'] == 'BUS'
    assert 'distance_heuristic_bus' in t_s1_s3['tags']
    assert 'stand_transfer' in t_s1_s3['tags']

    # 3. Bus -> Stand -> BUS
    t_b1_s1 = find_trip('B1', 'S1')
    print(f"B1->S1: {t_b1_s1['mode'] if t_b1_s1 else 'None'} (Expected BUS)")
    assert t_b1_s1['mode'] == 'BUS'
    assert 'bus_route' in t_b1_s1['tags']

    # 4. Rest -> Bus -> BUS (Depot Exit)
    t_r1_b1 = find_trip('R1', 'B1')
    print(f"R1->B1: {t_r1_b1['mode'] if t_r1_b1 else 'None'} (Expected BUS)")
    assert t_r1_b1['mode'] == 'BUS'
    assert 'depot_exit' in t_r1_b1['tags']

    # 5. Rest -> Stand (Close) -> WALK
    t_r1_s1 = find_trip('R1', 'S1')
    print(f"R1->S1 (40m): {t_r1_s1['mode'] if t_r1_s1 else 'None'} (Expected WALK)")
    assert t_r1_s1['mode'] == 'WALK'
    assert 'direct_walk' in t_r1_s1['tags']

    # 6. Rest -> Stand (Far) -> None
    t_r1_s3 = find_trip('R1', 'S3')
    print(f"R1->S3 (60m): {t_r1_s3['mode'] if t_r1_s3 else 'None'} (Expected None)")
    assert t_r1_s3 is None

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    run_test()
