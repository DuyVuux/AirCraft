import requests
import json

# Read input_sample.json
with open('../sample/input_sample.json', 'r', encoding='utf-8') as f:
    input_data = json.load(f)

# Get dataset ID (or create new one)
dataset_id = "1719bc98-d478-4d2c-8071-7008b19cb5cc"

# Update dataset with real data
response = requests.put(
    f'http://localhost:8000/api/datasets/{dataset_id}',
    json=input_data
)

print("Status Code:", response.status_code)
print("\nResponse:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Verify by reading back
print("\n" + "="*80)
print("VERIFYING: Reading back the data...")
print("="*80)

get_response = requests.get(f'http://localhost:8000/api/datasets/{dataset_id}')
data = get_response.json()

print("\n✅ Verification Results:")
print(f"  - trackingId: {data.get('trackingId')}")
print(f"  - aircrafts: {len(data.get('aircrafts', []))} items")
print(f"  - employees: {len(data.get('employees', []))} items")
print(f"  - hubs: {len(data.get('hubs', []))} items")
print(f"  - busStops: {len(data.get('busStops', []))} items")
print(f"  - busRoutes: {len(data.get('busRoutes', []))} items")

if data.get('matrixConfigs'):
    mc = data['matrixConfigs']
    print(f"  - matrixConfigs.distanceMatrix: {len(mc.get('distanceMatrix', []))} items")
    print(f"  - matrixConfigs.busTransitMatrix: {len(mc.get('busTransitMatrix', []))} items")
    print(f"  - matrixConfigs.walkingDistanceFromLocationToBusStop: {len(mc.get('walkingDistanceFromLocationToBusStop', []))} items")
    print(f"  - matrixConfigs.timeMatrix: {len(mc.get('timeMatrix', []))} items")

print("\n✅ Full data saved to: test_full_data_response.json")
with open('../sample/test_full_data_response.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
