import numpy as np
import hashlib
from typing import List, Dict, Tuple
from .floyd_warshall import floyd_warshall_numba, reconstruct_path


def compute_graph_hash(nodes: List[dict], edges: List[dict]) -> str:
    """
    Compute fingerprint của graph để detect changes
    
    Args:
        nodes: List of node dictionaries
        edges: List of edge dictionaries
    
    Returns:
        MD5 hash string representing the graph structure
    """
    node_str = ','.join(sorted([n['id'] for n in nodes]))
    edge_str = ','.join(sorted([
        f"{e['id']}:{e['nodeA']}-{e['nodeB']}:{e.get('distance', 0)}" 
        for e in edges
    ]))
    return hashlib.md5(f"{node_str}|{edge_str}".encode()).hexdigest()


def build_distance_matrix(
    nodes: List[dict], 
    edges: List[dict]
) -> Tuple[np.ndarray, Dict[str, int], Dict[int, str]]:
    """
    Build distance matrix from nodes and edges
    
    Args:
        nodes: List of node dictionaries with 'id' field
        edges: List of edge dictionaries with 'nodeA', 'nodeB', 'distance', 'directed'
    
    Returns:
        (distance_matrix, node_to_idx, idx_to_node)
    """
    n = len(nodes)
    
    # Create node ID mappings
    node_to_idx = {node['id']: idx for idx, node in enumerate(nodes)}
    idx_to_node = {idx: node['id'] for idx, node in enumerate(nodes)}
    
    # Initialize distance matrix with infinity
    dist = np.full((n, n), np.inf, dtype=np.float64)
    
    # Set diagonal to 0
    for i in range(n):
        dist[i, i] = 0
    
    # Fill in edges
    for edge in edges:
        i = node_to_idx[edge['nodeA']]
        j = node_to_idx[edge['nodeB']]
        distance = edge.get('distance', 1.0)
        
        # Handle multiple edges - keep minimum distance
        dist[i, j] = min(dist[i, j], distance)
        
        # Add reverse edge if undirected
        if not edge.get('directed', False):
            dist[j, i] = min(dist[j, i], distance)
    
    return dist, node_to_idx, idx_to_node


def compute_all_shortest_paths(
    nodes: List[dict], 
    edges: List[dict]
) -> Tuple[np.ndarray, np.ndarray, Dict[str, int], Dict[int, str]]:
    """
    Compute all-pairs shortest paths using Floyd-Warshall
    
    Args:
        nodes: List of node dictionaries
        edges: List of edge dictionaries
    
    Returns:
        (distance_matrix, next_matrix, node_to_idx, idx_to_node)
    """
    dist, node_to_idx, idx_to_node = build_distance_matrix(nodes, edges)
    n = len(nodes)
    
    # Run Floyd-Warshall with Numba
    dist, next_matrix = floyd_warshall_numba(dist, n)
    
    return dist, next_matrix, node_to_idx, idx_to_node


def get_shortest_path_info(
    i: int, 
    j: int, 
    dist_matrix: np.ndarray, 
    next_matrix: np.ndarray,
    idx_to_node: Dict[int, str],
    edges: List[dict]
) -> Tuple[float, List[str], List[str]]:
    """
    Get shortest path info between two nodes
    
    Args:
        i: Source node index
        j: Target node index
        dist_matrix: Distance matrix from Floyd-Warshall
        next_matrix: Next node matrix from Floyd-Warshall
        idx_to_node: Mapping from index to node ID
        edges: List of edge dictionaries
    
    Returns:
        (distance, node_path, edge_path)
    """
    distance = dist_matrix[i, j]
    
    if distance == np.inf:
        return float('inf'), [], []
    
    # Get node indices path
    idx_path = reconstruct_path(next_matrix, i, j)
    node_path = [idx_to_node[idx] for idx in idx_path]
    
    # Find edges
    edge_path = []
    for k in range(len(idx_path) - 1):
        src = idx_to_node[idx_path[k]]
        dst = idx_to_node[idx_path[k + 1]]
        
        # Find matching edge
        for edge in edges:
            if (edge['nodeA'] == src and edge['nodeB'] == dst) or \
               (not edge.get('directed', False) and edge['nodeA'] == dst and edge['nodeB'] == src):
                edge_path.append(edge['id'])
                break
    
    return distance, node_path, edge_path
