import json
import os
import re
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, Any

router = APIRouter()

DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "frontend" / "public" / "data"


class AirportCenter(BaseModel):
    lat: float
    lng: float


class AirportConfig(BaseModel):
    id: str
    name: str
    center: AirportCenter
    defaultZoom: int = 15
    dataFile: str


class AirportsConfig(BaseModel):
    airports: list[AirportConfig]
    defaultAirportId: str


class CreateAirportRequest(BaseModel):
    name: str
    center: AirportCenter
    defaultZoom: int = 15


class AirportData(BaseModel):
    trackingId: Optional[str] = None
    mapNodes: list[Any] = []
    mapEdges: list[Any] = []
    mapTrips: list[Any] = []
    aircrafts: list[Any] = []
    employees: list[Any] = []
    tasks: list[Any] = []
    hubs: list[Any] = []
    busStops: list[Any] = []
    busRoutes: list[Any] = []
    matrixConfigs: Optional[dict] = None
    timeMatrix: list[Any] = []
    sourceFiles: Optional[dict] = None


def load_airports_config() -> AirportsConfig:
    config_path = DATA_DIR / "airports.json"
    if not config_path.exists():
        return AirportsConfig(airports=[], defaultAirportId="")
    with open(config_path, "r", encoding="utf-8") as f:
        return AirportsConfig(**json.load(f))


def save_airports_config(config: AirportsConfig):
    config_path = DATA_DIR / "airports.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config.model_dump(), f, ensure_ascii=False, indent=2)


def generate_airport_id(name: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower().strip())
    slug = slug.strip('-')
    return slug or "airport"


@router.get("")
async def list_airports():
    config = load_airports_config()
    return config


@router.get("/{airport_id}")
async def get_airport(airport_id: str):
    config = load_airports_config()
    airport = next((a for a in config.airports if a.id == airport_id), None)
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    return airport


@router.get("/{airport_id}/data")
async def get_airport_data(airport_id: str):
    config = load_airports_config()
    airport = next((a for a in config.airports if a.id == airport_id), None)
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    
    data_path = DATA_DIR / airport.dataFile
    if not data_path.exists():
        # Return empty data structure if file doesn't exist yet
        return AirportData().model_dump()
        
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.post("/{airport_id}/data")
async def save_airport_data(airport_id: str, data: AirportData):
    config = load_airports_config()
    airport = next((a for a in config.airports if a.id == airport_id), None)
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    
    data_path = DATA_DIR / airport.dataFile
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data.model_dump(), f, ensure_ascii=False, indent=2)
    
    return {"success": True}


@router.post("")
async def create_airport(request: CreateAirportRequest):
    config = load_airports_config()
    
    airport_id = generate_airport_id(request.name)
    base_id = airport_id
    counter = 1
    while any(a.id == airport_id for a in config.airports):
        airport_id = f"{base_id}-{counter}"
        counter += 1
    
    data_file = f"{airport_id}.json"
    
    new_airport = AirportConfig(
        id=airport_id,
        name=request.name,
        center=request.center,
        defaultZoom=request.defaultZoom,
        dataFile=data_file
    )
    
    empty_data = AirportData()
    data_path = DATA_DIR / data_file
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(empty_data.model_dump(), f, ensure_ascii=False, indent=2)
    
    config.airports.append(new_airport)
    if not config.defaultAirportId:
        config.defaultAirportId = airport_id
    
    save_airports_config(config)
    
    return new_airport


@router.delete("/{airport_id}")
async def delete_airport(airport_id: str):
    config = load_airports_config()
    airport = next((a for a in config.airports if a.id == airport_id), None)
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    
    data_path = DATA_DIR / airport.dataFile
    if data_path.exists():
        os.remove(data_path)
    
    config.airports = [a for a in config.airports if a.id != airport_id]
    
    if config.defaultAirportId == airport_id:
        config.defaultAirportId = config.airports[0].id if config.airports else ""
    
    save_airports_config(config)
    
    return {"success": True}


@router.post("/upload")
async def upload_geojson(
    file: UploadFile = File(...),
    name: str = Form(...),
    centerLat: float = Form(...),
    centerLng: float = Form(...)
):
    content = await file.read()
    try:
        geojson_data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    
    map_nodes = []
    if "features" in geojson_data:
        for feature in geojson_data["features"]:
            if "geometry" not in feature:
                continue
            
            geom = feature["geometry"]
            props = feature.get("properties", {})
            
            osm_id = props.get("@id") or props.get("id") or feature.get("id", "")
            if not osm_id:
                continue
            
            if geom["type"] == "Point":
                lng, lat = geom["coordinates"]
            else:
                from functools import reduce
                def flatten_coords(coords):
                    if isinstance(coords[0], (int, float)):
                        return [coords]
                    return reduce(lambda a, b: a + flatten_coords(b), coords, [])
                
                all_coords = flatten_coords(geom["coordinates"])
                lng = sum(c[0] for c in all_coords) / len(all_coords)
                lat = sum(c[1] for c in all_coords) / len(all_coords)
            
            map_nodes.append({
                "id": osm_id,
                "name": osm_id.replace("way/", "Stand ").replace("node/", "Point "),
                "type": "aircraft_stand",
                "latitude": lat,
                "longitude": lng
            })
    
    config = load_airports_config()
    airport_id = generate_airport_id(name)
    base_id = airport_id
    counter = 1
    while any(a.id == airport_id for a in config.airports):
        airport_id = f"{base_id}-{counter}"
        counter += 1
    
    data_file = f"{airport_id}.json"
    
    new_airport = AirportConfig(
        id=airport_id,
        name=name,
        center=AirportCenter(lat=centerLat, lng=centerLng),
        defaultZoom=15,
        dataFile=data_file
    )
    
    airport_data = AirportData(mapNodes=map_nodes)
    data_path = DATA_DIR / data_file
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(airport_data.model_dump(), f, ensure_ascii=False, indent=2)
    
    config.airports.append(new_airport)
    save_airports_config(config)
    
    return new_airport
