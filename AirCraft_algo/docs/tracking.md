# Request/Response Tracking

✅ **Hoàn thành tính năng tracking**

## Cách hoạt động

Mỗi khi API `/api/NBP` được gọi:

1. **Extract tracking ID** từ input JSON (`trackingId` field)
2. **Chạy optimization pipeline**
3. **Save input + output** vào folder:
   ```
   data/
   └── YYYYMMDD_HHMMSS_trackingId/
       ├── input.json   # Request data
       └── output.json  # Solution data
   ```

## Ví dụ

**Input JSON:**
```json
{
  "trackingId": "REQ_20231205_001",
  "aircrafts": [...],
  "employees": [...]
}
```

**Folder created:**
```
data/20231205_161422_REQ_20231205_001/
├── input.json
└── output.json
```

## Implementation

### RequestTracker
- File: `src/utils/request_tracker.py`
- Method: `save_request(tracking_id, input_data, output_data)`
- Auto-creates timestamped folders

### NBPClient
- Auto-tracking enabled by default
- Prints: `[Tracking] Saved request to: data/...`

### Gitignore
- `data/` folder excluded from git

## Usage

```python
# Automatic tracking (no code changes needed)
client = NBPClient()
result = client.process(input_data)  # Auto-saves to data/
```

## Benefits

✓ Audit trail for all API calls  
✓ Easy debugging (compare input/output)  
✓ Historical data analysis  
✓ Reproducible test cases
