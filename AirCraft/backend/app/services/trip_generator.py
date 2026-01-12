from typing import List
from .graph_service import compute_all_shortest_paths, get_shortest_path_info


def generate_trips(nodes: List[dict], edges: List[dict], epsilon_walk: float = 50.0) -> List[dict]:
    """
    Generate trips between node pairs using Floyd-Warshall shortest paths
    
    Creates trips for (direction nodes are ONLY waypoints, never endpoints):
    1. Stand ↔ Stand (bidirectional) - Walk if <= epsilon, Bus if > epsilon (Simulated)
    2. Bus Stop → Stand (one-way) - Always Bus
    3. Rest Area → Bus Stop (one-way) - Always Bus (Depot Exit)
    4. Rest Area → Stand (one-way) - Walk ONLY if <= epsilon
    
    Args:
        nodes: List of node dictionaries with 'id', 'type', 'name' (optional)
        edges: List of edge dictionaries
        epsilon_walk: Distance threshold for walking (default 50.0)
    
    Returns:
        List of trip dictionaries with 'id', 'name', 'color', 'edgeIds', 'distance', 'path', 'mode', 'tags'
    """
    dist_matrix, next_matrix, node_to_idx, idx_to_node = compute_all_shortest_paths(nodes, edges)
    
    trips = []
    
    aircraft_stands = [n for n in nodes if n.get('type') == 'aircraft_stand']
    rest_areas = [n for n in nodes if n.get('type') == 'rest_area']
    bus_stops = [n for n in nodes if n.get('type') == 'bus_stop']
    
    # 1. Stand ↔ Stand (bidirectional)
    for i, from_node in enumerate(aircraft_stands):
        for j, to_node in enumerate(aircraft_stands):
            if i < j:
                trips.extend(_create_trip_pair(
                    from_node, to_node, dist_matrix, next_matrix, 
                    node_to_idx, idx_to_node, edges, '#3B82F6',
                    epsilon_walk=epsilon_walk,
                    base_tags=['stand_transfer']
                ))
    
    # 2. Bus Stop → Stand (one-way)
    for from_node in bus_stops:
        for to_node in aircraft_stands:
            trip = _create_trip(
                from_node, to_node, dist_matrix, next_matrix,
                node_to_idx, idx_to_node, edges, '#F59E0B',
                mode='BUS',
                tags=['bus_route']
            )
            if trip:
                trips.append(trip)
    
    # 3. Rest Area → Bus Stop (one-way)
    for from_node in rest_areas:
        for to_node in bus_stops:
            trip = _create_trip(
                from_node, to_node, dist_matrix, next_matrix,
                node_to_idx, idx_to_node, edges, '#10B981',
                mode='BUS', # Corrected: Rest -> Bus is vehicle leaving depot
                tags=['depot_exit']
            )
            if trip:
                trips.append(trip)
    
    # 4. Rest Area → Stand (one-way) - Walk ONLY if close
    for from_node in rest_areas:
        for to_node in aircraft_stands:
            trip = _create_trip(
                from_node, to_node, dist_matrix, next_matrix,
                node_to_idx, idx_to_node, edges, '#10B981',
                mode='WALK',
                epsilon_walk=epsilon_walk,
                tags=['direct_walk']
            )
            # Only keep if distance is within walking threshold
            if trip and trip['distance'] <= epsilon_walk:
                trips.append(trip)
    
    return trips


def _create_trip(
    from_node, to_node, dist_matrix, next_matrix, 
    node_to_idx, idx_to_node, edges, 
    color='#3B82F6', mode=None, epsilon_walk=50.0,
    tags=None
):
    """Create single trip from source to destination"""
    if from_node['id'] not in node_to_idx or to_node['id'] not in node_to_idx:
        return None
    
    src_idx = node_to_idx[from_node['id']]
    dst_idx = node_to_idx[to_node['id']]
    
    distance, node_path, edge_path = get_shortest_path_info(
        src_idx, dst_idx, dist_matrix, next_matrix, idx_to_node, edges
    )
    
    if distance == float('inf'):
        return None
    
    name_from = from_node.get('name') or from_node['id']
    name_to = to_node.get('name') or to_node['id']
    
    # Determine mode and tags if not provided
    trip_mode = mode
    trip_tags = tags or []
    
    if trip_mode is None:
        if distance <= epsilon_walk:
            trip_mode = 'WALK'
            trip_tags.append('proximity_walk')
        else:
            trip_mode = 'BUS'
            trip_tags.append('distance_heuristic_bus') # Flag as heuristic
    
    return {
        'id': f"trip_{from_node['id']}_to_{to_node['id']}",
        'name': f"{name_from} → {name_to}",
        'color': color,
        'edgeIds': edge_path,
        'distance': round(distance, 2),
        'path': node_path,
        'mode': trip_mode,
        'tags': trip_tags
    }


def _create_trip_pair(
    node_a, node_b, dist_matrix, next_matrix, 
    node_to_idx, idx_to_node, edges, 
    color='#3B82F6', epsilon_walk=50.0,
    base_tags=None
):
    """Create bidirectional trips between two nodes"""
    tags = base_tags or []
    trip_ab = _create_trip(
        node_a, node_b, dist_matrix, next_matrix, 
        node_to_idx, idx_to_node, edges, color, 
        epsilon_walk=epsilon_walk,
        tags=list(tags)
    )
    trip_ba = _create_trip(
        node_b, node_a, dist_matrix, next_matrix, 
        node_to_idx, idx_to_node, edges, color, 
        epsilon_walk=epsilon_walk,
        tags=list(tags)
    )
    return [t for t in [trip_ab, trip_ba] if t]

