"""
Constraint Builder Base Class - Abstract base for OR-Tools constraint components.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from ortools.sat.python import cp_model


class ConstraintBuilder(ABC):
    """
    Base class for OR-Tools constraint components.
    
    Each constraint builder is responsible for:
    1. Understanding relevant data from parsed context
    2. Accessing necessary decision variables
    3. Adding appropriate constraints to the CP model
    
    This design allows:
    - Independent testing of each constraint type
    - Easy enabling/disabling of constraint groups
    - Clear separation of concerns
    """
    
    def __init__(self, model: cp_model.CpModel):
        """
        Initialize constraint builder.
        
        Args:
            model: CP-SAT model to add constraints to
        """
        self.model = model
    
    @abstractmethod
    def build(self, data: Dict[str, Any], variables: Dict[str, Any]) -> None:
        """
        Build and add constraints to the model.
        
        Args:
            data: Parsed context data (tasks, employees, matrices, etc.)
            variables: Decision variables from ModelBuilder
                      - 'tasks': list of task variable dicts
                      - 'employees': employee data
                      - etc.
        """
        pass
    
    def __str__(self) -> str:
        """Return constraint builder name for logging."""
        return self.__class__.__name__
