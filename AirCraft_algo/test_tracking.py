"""
Test Request Tracking
"""
from src.utils.request_tracker import RequestTracker

# Test data
tracking_id = "TEST_001"
input_data = {
    "trackingId": "TEST_001",
    "aircrafts": [],
    "employees": []
}
output_data = {
    "solution": [],
    "droppedTasks": []
}

# Create tracker and save
tracker = RequestTracker()
saved_path = tracker.save_request(tracking_id, input_data, output_data)

print(f"✓ Saved test request to: {saved_path}")
print(f"  - input.json")
print(f"  - output.json")
