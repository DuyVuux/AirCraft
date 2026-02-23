"""
Time Utilities - Centralized time handling for aircraft maintenance scheduling.

All time-related functions should be imported from this module.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, List


# =============================================================================
# Time Conversion Functions
# =============================================================================

def parse_time(time_str: str) -> int:
    """
    Convert ISO 8601 time string to Unix timestamp (seconds).
    
    Handles formats:
    - "2024-12-05T08:00:00Z"
    - "2024-12-05T08:00:00+00:00"
    
    Returns:
        Unix timestamp in seconds (UTC)
    """
    return int(datetime.fromisoformat(time_str.replace('Z', '+00:00')).timestamp())


def timestamp_to_iso(timestamp: int) -> str:
    """
    Convert Unix timestamp to ISO 8601 UTC string.
    
    Args:
        timestamp: Unix timestamp in seconds
    
    Returns:
        ISO string with 'Z' suffix (UTC)
    """
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat().replace('+00:00', 'Z')


def timestamp_to_local_str(timestamp: int) -> str:
    """
    Convert Unix timestamp to local time string (HH:MM:SS).
    
    Useful for display/logging purposes.
    """
    if isinstance(timestamp, str):
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%H:%M:%S')
    else:
        return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')


# =============================================================================
# Time Normalization Functions (for solver internal use)
# =============================================================================

def normalize_time(timestamp: int, min_global_time: int) -> int:
    """
    Normalize timestamp relative to global start time.
    
    Used by solver to work with smaller numbers (0-based).
    
    Args:
        timestamp: Absolute Unix timestamp
        min_global_time: Earliest timestamp in the problem
    
    Returns:
        Normalized time (offset from min_global_time)
    """
    return timestamp - min_global_time


def denormalize_time(normalized: int, min_global_time: int) -> int:
    """
    Convert normalized time back to absolute timestamp.
    
    Args:
        normalized: Normalized time value
        min_global_time: Earliest timestamp used for normalization
    
    Returns:
        Absolute Unix timestamp
    """
    return normalized + min_global_time


# =============================================================================
# Duration Formatting
# =============================================================================

def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Examples:
        45 -> "45s"
        90 -> "1m30s"
        3661 -> "1h1m"
    """
    if seconds < 0:
        return f"-{format_duration(-seconds)}"
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}m{secs}s" if secs > 0 else f"{mins}m"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h{mins}m" if mins > 0 else f"{hours}h"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class TimeWindow:
    """Time window with ISO start and end times."""
    start: str
    end: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeWindow':
        return cls(
            start=data['start'],
            end=data['end']
        )
    
    def get_start_timestamp(self) -> int:
        """Get start time as Unix timestamp."""
        return parse_time(self.start)
    
    def get_end_timestamp(self) -> int:
        """Get end time as Unix timestamp."""
        return parse_time(self.end)


@dataclass
class TimeEntry:
    """Task duration configuration entry."""
    taskCode: str
    role: str
    certificates: List[str]
    aircraftId: str
    timeProcess: int
    level: int = 1

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeEntry':
        return cls(
            taskCode=data['taskCode'],
            role=data['role'],
            certificates=data.get('certificates', []),
            aircraftId=data['aircraftId'],
            timeProcess=data['timeProcess'],
            level=data.get('level', 1)
        )


