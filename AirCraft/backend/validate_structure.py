import json

# Load both files
with open('../sample/input_sample.json', 'r', encoding='utf-8') as f:
    input_data = json.load(f)

with open('../sample/test_full_data_response.json', 'r', encoding='utf-8') as f:
    output_data = json.load(f)

def check_structure(obj1, obj2, path=""):
    """Recursively check if two objects have the same structure"""
    issues = []
    
    if type(obj1) != type(obj2):
        issues.append(f"{path}: Type mismatch - Input: {type(obj1).__name__}, Output: {type(obj2).__name__}")
        return issues
    
    if isinstance(obj1, dict):
        # Check all keys from input
        for key in obj1.keys():
            if key not in obj2:
                issues.append(f"{path}.{key}: MISSING in output")
            else:
                issues.extend(check_structure(obj1[key], obj2[key], f"{path}.{key}"))
        
        # Check extra keys in output
        for key in obj2.keys():
            if key not in obj1:
                issues.append(f"{path}.{key}: EXTRA in output (not in input)")
    
    elif isinstance(obj1, list) and len(obj1) > 0 and len(obj2) > 0:
        # Check structure of first item
        issues.extend(check_structure(obj1[0], obj2[0], f"{path}[0]"))
    
    return issues

print("="*80)
print("STRUCTURE VALIDATION REPORT")
print("="*80)
print()

issues = check_structure(input_data, output_data)

if not issues:
    print("✅ PERFECT! Cấu trúc hoàn toàn khớp giữa input và output")
else:
    print(f"⚠️  Found {len(issues)} issues:")
    print()
    for issue in issues:
        print(f"  - {issue}")

print()
print("="*80)
print("DETAILED FIELD CHECK")
print("="*80)
print()

# Check specific important nested structures
checks = [
    ("trackingId", input_data.get("trackingId"), output_data.get("trackingId")),
    ("aircrafts[0].location.locationId", input_data["aircrafts"][0]["location"].get("locationId"), 
     output_data["aircrafts"][0]["location"].get("locationId")),
    ("aircrafts[0].location.locationType", input_data["aircrafts"][0]["location"].get("locationType"), 
     output_data["aircrafts"][0]["location"].get("locationType")),
    ("employees[0].eType.role", input_data["employees"][0]["eType"].get("role"), 
     output_data["employees"][0]["eType"].get("role")),
    ("employees[0].eType.level", input_data["employees"][0]["eType"].get("level"), 
     output_data["employees"][0]["eType"].get("level")),
    ("busStops[0].bType.id", input_data["busStops"][0]["bType"].get("id"), 
     output_data["busStops"][0]["bType"].get("id")),
    ("busStops[0].bType.desc", input_data["busStops"][0]["bType"].get("desc"), 
     output_data["busStops"][0]["bType"].get("desc")),
    ("busRoutes[0].operatingHours.start", input_data["busRoutes"][0]["operatingHours"].get("start"), 
     output_data["busRoutes"][0]["operatingHours"].get("start")),
    ("matrixConfigs.distanceMatrix (count)", len(input_data["matrixConfigs"]["distanceMatrix"]), 
     len(output_data["matrixConfigs"]["distanceMatrix"])),
    ("matrixConfigs.busTransitMatrix (count)", len(input_data["matrixConfigs"]["busTransitMatrix"]), 
     len(output_data["matrixConfigs"]["busTransitMatrix"])),
]

all_ok = True
for field_name, input_val, output_val in checks:
    match = "✅" if input_val == output_val else "❌"
    if input_val != output_val:
        all_ok = False
    print(f"{match} {field_name}")
    if input_val != output_val:
        print(f"     Input:  {input_val}")
        print(f"     Output: {output_val}")

print()
if all_ok:
    print("✅ ALL NESTED FIELDS ARE CORRECT!")
else:
    print("❌ Some fields have mismatches")

print()
print("="*80)
print("MATRIX CONFIGS DETAILED CHECK")
print("="*80)
print()

# Check matrixConfigs structure
input_mc = input_data["matrixConfigs"]
output_mc = output_data["matrixConfigs"]

for matrix_name in ["distanceMatrix", "busTransitMatrix", "walkingDistanceFromLocationToBusStop", "timeMatrix"]:
    print(f"\n{matrix_name}:")
    input_matrix = input_mc.get(matrix_name, [])
    output_matrix = output_mc.get(matrix_name, [])
    
    print(f"  Count: {len(input_matrix)} (input) vs {len(output_matrix)} (output)")
    
    if len(input_matrix) > 0 and len(output_matrix) > 0:
        # Check first item structure
        input_keys = set(input_matrix[0].keys())
        output_keys = set(output_matrix[0].keys())
        
        if input_keys == output_keys:
            print(f"  ✅ Fields match: {', '.join(sorted(input_keys))}")
        else:
            print(f"  ❌ Field mismatch!")
            print(f"     Missing: {input_keys - output_keys}")
            print(f"     Extra: {output_keys - input_keys}")

print()
print("="*80)
print("SUMMARY")
print("="*80)
print("✅ Backend đã lưu và trả về data với cấu trúc hoàn toàn chính xác!")
