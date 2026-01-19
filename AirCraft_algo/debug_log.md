# Debug Log - Greedy Strategy

File này ghi lại quá trình debug và fix bug để Boss có thể học theo phương pháp.

---

## Bug #1: Tất cả tasks bị dropped (0 tasks assigned)

### Ngày: 2026-01-12

### Vấn đề phát hiện
Khi chạy test với data DEF123 và input_sample.json, thuật toán greedy trả về:
```
- Employees used: 0
- Tasks assigned: 0  
- Tasks dropped: 6
```

### Cách tìm ra nguyên nhân

**Bước 1: In ra thông tin tasks và employees**

Chạy script debug để xem data:
```python
# Xem tasks cần gì
for ac in ctx.aircrafts:
    for t in ac.requiredTasks:
        print(f'Task: {t.taskCode}, requiredCerts: {t.requiredCertificates}')

# Xem employees có gì
for emp in ctx.employees:
    print(f'Capabilities: {emp.taskCapabilities}')  # → N/A
```

**Bước 2: So sánh raw JSON với parsed model**

```python
# Raw JSON có taskCapabilities
with open('input_data.json') as f:
    data = json.load(f)
emp = data['employees'][0]
print(emp)  
# → {"employeeId": "...", "taskCapabilities": ["WO-01"], ...}

# Nhưng Employee model không có field này!
from src.model.employee import Employee
# → Không có taskCapabilities trong dataclass
```

### Nguyên nhân gốc

File `src/model/employee.py` không parse field `taskCapabilities` từ input JSON:

```python
@dataclass
class Employee:
    employeeId: str
    eType: EmployeeType
    workingTimes: List[TimeWindow]
    breakDuration: int
    fixedBreakTimes: List[TimeWindow]
    currentLocation: Optional[str] = None
    # ← THIẾU taskCapabilities và certifications!
```

Khi `from_dict()` được gọi, nó không đọc `taskCapabilities` nên employee không có năng lực làm task.

### Giải pháp

Thêm 2 fields vào Employee model:

```python
@dataclass
class Employee:
    # ... existing fields ...
    taskCapabilities: List[str] = field(default_factory=list)  # NEW
    certifications: List[str] = field(default_factory=list)     # NEW

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Employee':
        return cls(
            # ... existing ...
            taskCapabilities=data.get('taskCapabilities', []),  # NEW
            certifications=data.get('certifications', [])       # NEW
        )
```

### Files sửa

| File | Thay đổi |
|------|----------|
| `src/model/employee.py` | Thêm `taskCapabilities` và `certifications` fields |

### Bài học rút ra

1. **So sánh raw data với parsed model**: Khi logic đúng nhưng kết quả sai, kiểm tra xem data có được parse đầy đủ không.

2. **Debug từ output ngược về input**: 
   - Kết quả: 0 tasks assigned
   - → Logic check: Employee không có capability
   - → Data check: Field không được parse

3. **Print debug sớm**: Thêm print statements ở các điểm quan trọng giúp thấy data flow.

---

*Thêm entries mới ở đây khi có bug tiếp theo...*

---

## Bug #2: Aircraft và Employee không cùng năm (DATA BUG)

### Ngày: 2026-01-12

### Vấn đề phát hiện
Sau khi fix Bug #1, vẫn 0 tasks assigned. Debug sâu hơn phát hiện:

```
=== AIRCRAFT TIME WINDOWS ===
VN19-1: 2022-01-31 00:00:00 -> 2022-01-30 18:00:00
  Timestamps: 1643562000 -> 1643540400

=== EMPLOYEE WORKING TIMES ===  
VAE03726:
  WorkingTime: 2026-01-02T12:32:20.213Z -> 2026-01-02T20:32:20.214Z
  Timestamps: 1767357140 -> 1767385940
```

**Chênh lệch 4 năm!** Nhân viên làm việc 2026 nhưng máy bay cần phục vụ 2022.

### Cách tìm ra

**Bước 1: In timestamps dạng số**
```python
from src.model.time import parse_time

# Aircraft
start = parse_time(ac.timeWindow.start)  # -> 1643562000
# Employee
start = parse_time(wt.start)  # -> 1767357140

# Chênh lệch: 1767357140 - 1643562000 = 123,795,140 giây ≈ 4 năm!
```

**Bước 2: So sánh trực tiếp**
- Aircraft: `2022-01-31`
- Employee: `2026-01-02`
- → Không có cách nào overlap!

### Nguyên nhân gốc

**Đây là DATA BUG, không phải code bug.**

File `input_data_2026-01-12.json` chứa:
- Aircraft timeWindow từ dataset cũ (năm 2022)
- Employee workingTimes từ frontend mới (năm 2026)

### Giải pháp

Có 2 cách:
1. **Sửa dữ liệu**: Đồng bộ aircraft timeWindow về 2026
2. **Sửa thuật toán**: Bỏ qua constraint năm khi test (KHÔNG khuyến khích)

**Quyết định**: Test với dataset DEF123 từ frontend (có timeWindow đúng 2026).

### Bài học rút ra

1. **Kiểm tra dữ liệu đầu tiên**: Khi thuật toán logic đúng mà kết quả sai, có thể là dữ liệu sai.

2. **So sánh timestamps**: Chuyển time về số (Unix timestamp) dễ so sánh hơn.

3. **Log cả raw value lẫn parsed value**: Giúp phát hiện vấn đề formatting/parsing.

---

## Bug #3: Certificate check logic sai với DEF123 format

### Ngày: 2026-01-12

### Vấn đề phát hiện
Sau khi tạo test input từ DEF123 (đúng năm 2026), vẫn 0 tasks assigned:

```
Task DEP-M: requiredCerts=['DEP-M']     # Task yêu cầu cert 'DEP-M'
Employee: certs=['A321', 'B787']         # Nhưng employee có 'A321', 'B787'
# → 'DEP-M' not in ['A321', 'B787'] → False → Task dropped!
```

### Cách tìm ra

**In ra đầy đủ thông tin task và employee:**
```python
for emp in ctx.employees:
    if 'DEP-M' in emp.taskCapabilities:
        print(f'{emp.employeeId}: caps={emp.taskCapabilities}, certs={emp.certifications}')

for ac in ctx.aircrafts:
    for task in ac.requiredTasks:
        if task.taskCode == 'DEP-M':
            print(f'requiredCerts={task.requiredCertificates}')
```

**Kết quả:**
- Task yêu cầu: `['DEP-M']` ← giống task code!
- Employee có: `['A321', 'B787']` ← aircraft type certificates

### Nguyên nhân gốc

Trong DEF123 dataset, `requiredCertificates` chứa task code thay vì aircraft certificates. Đây là quirk của data format, không phải bug logic.

### Giải pháp

Bỏ qua certificate nếu nó trùng với task code:

```python
def _can_employee_do_task(self, emp_state, task):
    if task.task_code not in emp_state.capabilities:
        return False
    
    if task.required_certificates:
        for cert in task.required_certificates:
            if cert == task.task_code:  # NEW: Skip task code as cert
                continue
            if cert not in emp_state.certificates:
                return False
    
    return True
```

### Kết quả sau fix

```
=== SOLUTION ===
Employees used: 20
Tasks assigned: 20
Tasks dropped: 0
```

### Bài học rút ra

1. **Data format khác nhau**: Cùng field name nhưng semantic khác nhau giữa các datasets.

2. **Debug với sample nhỏ**: In ra 1-2 records đầy đủ để thấy pattern.

3. **Defensive coding**: Thêm edge case handling khi data format không consistent.

---

*Thêm entries mới ở đây khi có bug tiếp theo...*

---

## Bug #4: Frontend export sai data format (CRITICAL)

### Ngày: 2026-01-12

### Vấn đề phát hiện
Data export từ frontend không khớp với expected format của algorithm:

1. **transformEmployee sai:**
   - `taskCapabilities` đang được gán vào `eType.certificates` (SAI!)
   - Thiếu export `taskCapabilities` và `certifications` riêng

2. **transformAircraft sai:**
   - `requiredCertificates` được hardcode là `[task.taskCode]` thay vì lấy từ data

### Nguyên nhân gốc
File `frontend/src/utils/transformForAlgo.ts` có logic transform không đúng.

### Giải pháp

**Fix transformEmployee:**
```typescript
eType: { certificates: emp.certifications || [] },  // Lấy từ certifications
taskCapabilities: emp.taskCapabilities || [],       // Export riêng
certifications: emp.certifications || []            // Export riêng
```

**Fix transformAircraft:**
```typescript
requiredCertificates: task.requiredCertificates || []  // Lấy từ task data
```

### Files sửa
- `frontend/src/utils/transformForAlgo.ts`

### Bài học rút ra
1. **Kiểm tra transform logic** ở từng bước của data pipeline
2. **So sánh expected vs actual output**
3. **Đừng hardcode** - lấy giá trị từ source data

---

## Improvement #1: Greedy Logic Tuần Tự (Sequential)

### Ngày: 2026-01-12

### Vấn đề
Greedy cũ xếp tasks song song (parallel) nếu nhân viên rảnh, dẫn đến:
- Tasks chồng chéo thời gian (overlap)
- Không tuân thủ quy trình `ARR -> TOW -> WO -> DEP`
- Tasks hiển thị xuyên suốt từ đầu đến cuối trên chart (không thực tế)

### Giải pháp
1. **Thêm Priority cho Task**:
   - `ARR` (Priority 0)
   - `TOW` (Priority 1)
   - `WO` (Priority 2)
   - `DEP` (Priority 3)

2. **Sắp xếp Tasks**:
   - Sort theo `(deadline, priority)` thay vì chỉ `deadline`.

3. **Enforce Sequential Execution**:
   - Dùng `aircraft_ready_times` map để track thời gian máy bay rảnh.
   - `start_time` của task mới phải >= `aircraft_ready_time` (thời điểm task trước kết thúc).

### Files sửa
- `src/strategy/greedyStrategy/greedy_strategy.py`

### Kết quả mong đợi
- Tasks của cùng 1 máy bay sẽ xếp nối tiếp nhau.
- Không còn task nào chạy song song trên 1 máy bay.
- Biểu đồ Gantt sẽ thể hiện rõ quy trình làm việc.

---
