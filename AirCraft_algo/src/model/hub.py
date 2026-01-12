from dataclasses import dataclass
from typing import Dict, Any
from src.model.location import Location

@dataclass
class Hub:
    hubId: str
    location: Location

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Hub':
        return cls(
            hubId=data['hubId'],
            location=Location.from_dict(data['location'])
        )
