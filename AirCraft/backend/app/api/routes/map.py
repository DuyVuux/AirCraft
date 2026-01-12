from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.graph_service import compute_graph_hash
from app.services.trip_generator import generate_trips

router = APIRouter()


class Node(BaseModel):
    id: str
    type: str
    latitude: float
    longitude: float
    name: Optional[str] = None


class Edge(BaseModel):
    id: str
    nodeA: str
    nodeB: str
    distance: float
    directed: bool = False


class GenerateTripsRequest(BaseModel):
    airportId: str
    nodes: List[Node]
    edges: List[Edge]
    cachedHash: Optional[str] = None
    epsilon_walk: float = 50.0  # Default 50m threshold for walking


@router.post("/generate-trips")
async def generate_trips_endpoint(request: GenerateTripsRequest):
    """
    Generate trips using Floyd-Warshall shortest paths
    
    Auto-generates trips between:
    - All pairs of aircraft stands (bidirectional)
    - Aircraft stands to rest areas (one-way)
    - Aircraft stands to bus stops (one-way)
    
    Returns cached flag if graph hash matches to avoid recomputation on frontend
    """
    nodes_dict = [n.dict() for n in request.nodes]
    edges_dict = [e.dict() for e in request.edges]
    
    # Compute graph hash
    current_hash = compute_graph_hash(nodes_dict, edges_dict)
    
    # Check if cache is valid
    if request.cachedHash == current_hash:
        return {
            "cached": True, 
            "cacheKey": current_hash, 
            "trips": []
        }
    
    # Generate trips
    try:
        trips = generate_trips(nodes_dict, edges_dict, epsilon_walk=request.epsilon_walk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate trips: {str(e)}")
    
    return {
        "cached": False,
        "cacheKey": current_hash,
        "trips": trips
    }
