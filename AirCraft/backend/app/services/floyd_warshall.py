import numpy as np
from numba import jit
from typing import Tuple, List


@jit(nopython=True)
def floyd_warshall_numba(dist: np.ndarray, n: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Floyd-Warshall algorithm with Numba JIT compilation
    
    Args:
        dist: Distance matrix (n x n)
        n: Number of nodes
    
    Returns:
        (distance_matrix, next_matrix for path reconstruction)
    """
    # Initialize next matrix for path reconstruction
    next_matrix = np.full((n, n), -1, dtype=np.int32)
    
    # Set next matrix for direct edges
    for i in range(n):
        for j in range(n):
            if i != j and dist[i, j] != np.inf:
                next_matrix[i, j] = j
    
    # Floyd-Warshall main loop
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i, k] + dist[k, j] < dist[i, j]:
                    dist[i, j] = dist[i, k] + dist[k, j]
                    next_matrix[i, j] = next_matrix[i, k]
    
    return dist, next_matrix


def reconstruct_path(next_matrix: np.ndarray, i: int, j: int) -> List[int]:
    """
    Reconstruct path from next matrix
    
    Args:
        next_matrix: Next node matrix from Floyd-Warshall
        i: Source node index
        j: Target node index
    
    Returns:
        List of node indices representing the path
    """
    if next_matrix[i, j] == -1:
        return []
    
    path = [i]
    while i != j:
        i = next_matrix[i, j]
        path.append(i)
    return path
