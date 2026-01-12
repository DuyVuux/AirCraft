"""
Request/Response Tracking - Save API requests and responses with tracking ID.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any


class RequestTracker:
    """
    Tracks API requests and responses by saving them to disk with tracking IDs.
    
    Directory structure:
        data/
        └── {trackingId}/
            ├── input.json
            ├── input_description.md
            ├── output.json
            └── output_summary.md
    """
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    def get_tracking_dir(self, tracking_id: str) -> str:
        """Get the directory path for a tracking ID"""
        return os.path.join(self.base_dir, tracking_id)
    
    def save_request(self, tracking_id: str, input_data: Dict[str, Any], 
                     output_data: Dict[str, Any]) -> str:
        """
        Save input and output for a request.
        
        Args:
            tracking_id: Unique tracking identifier
            input_data: Request input (Context dict)
            output_data: Response output (Solution dict)
            
        Returns:
            Directory path for this tracking ID
        """
        # Create tracking ID directory
        tracking_dir = self.get_tracking_dir(tracking_id)
        os.makedirs(tracking_dir, exist_ok=True)
        
        # Save input
        input_path = os.path.join(tracking_dir, "input.json")
        with open(input_path, 'w', encoding='utf-8') as f:
            json.dump(input_data, f, indent=2, ensure_ascii=False)
        
        # Save output
        output_path = os.path.join(tracking_dir, "output.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        return tracking_dir

