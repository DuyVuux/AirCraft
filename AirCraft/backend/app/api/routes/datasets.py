from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
import os
import shutil
from datetime import datetime
import uuid

router = APIRouter()

# Data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "data", "datasets")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

class DatasetMeta(BaseModel):
    id: str
    name: str
    createdAt: str
    updatedAt: str
    itemCounts: Dict[str, int]

class MatrixConfigs(BaseModel):
    distanceMatrix: List[Any] = []
    busTransitMatrix: List[Any] = []
    walkingDistanceFromLocationToBusStop: List[Any] = []
    timeMatrix: List[Any] = []

class DatasetData(BaseModel):
    trackingId: Optional[str] = None
    aircrafts: List[Any] = []
    hubs: List[Any] = []
    employees: List[Any] = []
    busStops: List[Any] = []
    busRoutes: List[Any] = []
    matrixConfigs: Optional[MatrixConfigs] = None
    tasks: List[Any] = []
    timeMatrix: List[Any] = []

class CreateDatasetRequest(BaseModel):
    name: str

def get_dataset_path(dataset_id: str) -> str:
    return os.path.join(DATA_DIR, f"{dataset_id}.json")

def load_dataset_file(dataset_id: str) -> Optional[Dict[str, Any]]:
    path = get_dataset_path(dataset_id)
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading dataset {dataset_id}: {e}")
        return None

def save_dataset_file(dataset_id: str, data: Dict[str, Any]):
    path = get_dataset_path(dataset_id)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@router.get("/", response_model=List[DatasetMeta])
async def list_datasets():
    datasets = []
    if not os.path.exists(DATA_DIR):
        return []
    
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            dataset_id = filename[:-5]
            data = load_dataset_file(dataset_id)
            if data and "meta" in data:
                datasets.append(DatasetMeta(**data["meta"]))
    
    # Sort by updatedAt desc
    datasets.sort(key=lambda x: x.updatedAt, reverse=True)
    return datasets

@router.post("/", response_model=Dict[str, Any])
async def create_dataset(request: CreateDatasetRequest):
    dataset_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    meta = {
        "id": dataset_id,
        "name": request.name,
        "createdAt": now,
        "updatedAt": now,
        "itemCounts": {
            "tasks": 0,
            "employees": 0,
            "hubs": 0,
            "aircrafts": 0,
            "busStops": 0,
            "busRoutes": 0,
            "timeMatrix": 0
        }
    }
    
    data = {
        "trackingId": None,
        "tasks": [],
        "employees": [],
        "hubs": [],
        "aircrafts": [],
        "busStops": [],
        "busRoutes": [],
        "matrixConfigs": {
            "distanceMatrix": [],
            "busTransitMatrix": [],
            "walkingDistanceFromLocationToBusStop": [],
            "timeMatrix": []
        },
        "timeMatrix": []
    }
    
    full_content = {
        "meta": meta,
        "data": data
    }
    
    save_dataset_file(dataset_id, full_content)
    return {"meta": meta, "data": data}

@router.get("/{dataset_id}", response_model=DatasetData)
async def get_dataset(dataset_id: str):
    content = load_dataset_file(dataset_id)
    if not content or "data" not in content:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return content["data"]

@router.put("/{dataset_id}")
async def update_dataset(dataset_id: str, data: DatasetData):
    content = load_dataset_file(dataset_id)
    if not content:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Update data
    content["data"] = data.dict()
    
    # Update meta
    now = datetime.now().isoformat()
    content["meta"]["updatedAt"] = now
    content["meta"]["itemCounts"] = {
        "tasks": len(data.tasks),
        "employees": len(data.employees),
        "hubs": len(data.hubs),
        "aircrafts": len(data.aircrafts),
        "busStops": len(data.busStops),
        "busRoutes": len(data.busRoutes),
        "timeMatrix": len(data.timeMatrix)
    }
    
    save_dataset_file(dataset_id, content)
    return {"status": "success", "meta": content["meta"]}

@router.post("/{dataset_id}/rename")
async def rename_dataset(dataset_id: str, name: Dict[str, str]):
    new_name = name.get("name")
    if not new_name:
        raise HTTPException(status_code=400, detail="Name is required")

    content = load_dataset_file(dataset_id)
    if not content:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    content["meta"]["name"] = new_name
    content["meta"]["updatedAt"] = datetime.now().isoformat()
    
    save_dataset_file(dataset_id, content)
    return {"status": "success", "meta": content["meta"]}

@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str):
    path = get_dataset_path(dataset_id)
    if os.path.exists(path):
        os.remove(path)
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Dataset not found")
