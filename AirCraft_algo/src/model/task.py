from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Task:
    taskCode: str
    requiredCertificates: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    minLevel: int = 1
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        return cls(
            taskCode=data['taskCode'],
            requiredCertificates=data.get('requiredCertificates', []),
            dependencies=data.get('dependencies', []),
            minLevel=data.get('minLevel', 1)
        )

