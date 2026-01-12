from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class Location:
    longitude: float
    latitude: float
    locationId: Optional[str] = None
    locationType: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        return cls(
            longitude=data['longitude'],
            latitude=data['latitude'],
            locationId=data.get('locationId'),
            locationType=data.get('locationType')
        )

