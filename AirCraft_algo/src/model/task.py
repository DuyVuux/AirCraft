from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Task:
    taskCode: str
    requiredCertificates: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        return cls(
            taskCode=data['taskCode'],
            requiredCertificates=data.get('requiredCertificates', [])
        )
