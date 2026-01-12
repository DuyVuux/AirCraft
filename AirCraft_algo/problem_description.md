# Tài Liệu Phân Tích Bài Toán: Lập Lịch Bảo Trì Máy Bay Tối Ưu

## 1. Tổng Quan
Dự án nhằm giải quyết bài toán tối ưu hóa nguồn lực nhân sự cho việc bảo trì máy bay tại sân bay. Mục tiêu là đảm bảo tất cả các máy bay được bảo trì đúng hạn với số lượng nhân viên ít nhất có thể.

## 2. Các Thực Thể Chính (Entities)

### 2.1. Máy Bay (Aircraft)
- **Vị trí (Location):** Mỗi máy bay đậu tại một vị trí xác định (có thể là tọa độ hoặc ID bãi đỗ).
- **Khung thời gian (Time Window - TW):** Khoảng thời gian cho phép để thực hiện việc bảo trì.
  - `Earliest Start Time`: Thời điểm sớm nhất có thể bắt đầu.
  - `Latest Finish Time`: Thời điểm muộn nhất phải hoàn thành tất cả các task.
- **Danh sách công việc (Required Tasks):** Các hạng mục bảo trì cần thực hiện cho máy bay này.

### 2.2. Công Việc (Task)
- **Loại công việc:** Xác định kỹ năng chuyên môn cần thiết.
- **Thời gian thực hiện (Duration):** Thời gian cần thiết để hoàn thành công việc.
- **Ràng buộc:** Một số task có thể phụ thuộc lẫn nhau (ví dụ: Task A phải xong trước Task B) - *Cần xác nhận thêm nếu có ràng buộc thứ tự này, hiện tại giả định là độc lập hoặc theo thứ tự danh sách.*

### 2.3. Nhân Viên Bảo Trì (Maintenance Staff)
- **Vai trò (Role):** Mỗi nhân viên có một vai trò cụ thể (ví dụ: Thợ điện, Thợ cơ khí...).
- **Cấp độ (Level):** Phản ánh trình độ và tốc độ làm việc của nhân viên. Level càng cao (hoặc quy định cụ thể) thì thời gian thực hiện task càng ngắn.
- **Kỹ năng (Capabilities):** Được xác định bởi Role. Khả năng thực hiện task cụ thể phụ thuộc vào Role và Level được định nghĩa trong `timeMatrix`.
- **Di chuyển:** Nhân viên cần di chuyển giữa các vị trí máy bay và các trạm nghỉ (Hubs). Thời gian di chuyển được lấy từ `distanceMatrix`.

### 2.4. Trạm Nghỉ (Hub)
- **Vị trí:** Nơi nhân viên nghỉ ngơi hoặc chờ việc.
- **Tọa độ:** Kinh độ, vĩ độ.

## 3. Mô Tả Quy Trình Hoạt Động
1. **Phân công:** Hệ thống phân công nhân viên vào các task cụ thể trên các máy bay dựa trên Role của họ.
2. **Thực hiện:**
   - Nhân viên đến vị trí máy bay.
   - Thực hiện task trong khoảng thời gian `Duration`.
   - Task phải được thực hiện (hoặc hoàn thành) trong `Time Window` của máy bay đó.
3. **Di chuyển:** Sau khi hoàn thành task ở máy bay A, nhân viên di chuyển sang máy bay B để làm task tiếp theo (nếu được phân công). Thời gian di chuyển phải được tính toán vào tổng thời gian.

## 4. Mục Tiêu (Objectives)
Bài toán có hai mục tiêu chính theo thứ tự ưu tiên:
1. **Mục tiêu bắt buộc (Hard Constraint):** Hoàn thành **100%** các task được yêu cầu cho tất cả các máy bay.
2. **Mục tiêu tối ưu (Optimization):** Sử dụng **ít nhất** số lượng nhân viên bảo trì.

## 5. Các Ràng Buộc (Constraints)
1. **Ràng buộc về Kỹ năng:** Nhân viên chỉ được làm task mà Role của họ cho phép.
2. **Ràng buộc về Thời gian (Time Window):**
   - Việc bảo trì cho một máy bay phải diễn ra trong khung giờ [Start, End] của máy bay đó.
   - (Cần làm rõ: *Tất cả các task phải hoàn thành trước End Time* hay *Chỉ cần bắt đầu trước End Time*? Giả định hiện tại: Phải hoàn thành trước End Time).
3. **Ràng buộc về Không gian & Thời gian di chuyển:**
   - `Thời gian bắt đầu task tại B` >= `Thời gian kết thúc task tại A` + `Thời gian di chuyển từ A đến B`.
4. **Ràng buộc về Tài nguyên:** Một nhân viên chỉ có thể làm 1 task tại 1 thời điểm.

## 6. Đầu Vào & Đầu Ra Dự Kiến

### Đầu vào (Input)
- `trackingId`: Mã định danh duy nhất cho yêu cầu lập lịch.
- `aircrafts`: Danh sách Máy bay.
  - `aircraftId`: ID máy bay.
  - `aType`: Loại máy bay (object).
  - `location`: Thông tin vị trí (object).
    - `locationId`: Mã vị trí.
    - `locationType`: Loại vị trí (ví dụ: GATE, HANGAR).
    - `longitude`: Kinh độ.
    - `latitude`: Vĩ độ.
  - `timeWindow`: `{start, end}` (định dạng UTC ISO 8601).
  - `requiredTasks`: Danh sách các task cần làm.
    - `taskCode`: Mã task.
    - `minLevel`: Cấp độ tối thiểu của nhân viên để thực hiện task này.
- `hubs`: Danh sách Trạm nghỉ.
  - `hubId`: ID trạm.
  - `location`: Thông tin vị trí (object).
    - `locationId`: Mã vị trí.
    - `locationType`: Loại vị trí (ví dụ: HUB, REST_AREA).
    - `longitude`: Kinh độ.
    - `latitude`: Vĩ độ.
- `employees`: Danh sách Nhân viên.
  - `employeeId`: ID nhân viên.
  - `eType`: Thông tin loại nhân viên, bao gồm `{role, level}`.
  - `workingTimes`: Danh sách khung giờ làm việc `{start, end}` (UTC ISO 8601).
  - `breakDuration`: Thời gian nghỉ ngơi linh hoạt (tính bằng giây).
  - `fixedBreakTimes`: Danh sách khung giờ nghỉ ngơi bắt buộc `{start, end}` (UTC ISO 8601).
- `matrixConfigs`:
  - `distanceMatrix`: Danh sách các object `{srcCode, destCode, travelTime}` mô tả thời gian di chuyển (tính bằng giây).
  - `timeMatrix`: Danh sách cấu hình thời gian cho từng task (dạng phẳng).
    - `taskCode`: Mã task.
    - `role`: Tên role.
    - `level`: Cấp độ nhân viên.
    - `aircraftId`: ID máy bay (thời gian có thể khác nhau tùy máy bay).
    - `timeProcess`: Thời gian thực hiện (tính bằng giây).

### Đầu ra (Output)
### Đầu ra (Output)
- `solution`:
  - `[employeeId]`: Thông tin và lịch trình của nhân viên.
    - `level`: Cấp độ của nhân viên.
    - `assignment`: Danh sách các hoạt động (Task). Khoảng thời gian giữa 2 hoạt động liên tiếp bao gồm thời gian di chuyển, nghỉ ngơi và chờ đợi. Mỗi hoạt động gồm:
      - `type`: Loại hoạt động (thường là TASK).
      - `locationId`: Vị trí thực hiện.
      - `startTime`: Thời gian bắt đầu (UTC ISO 8601).
      - `endTime`: Thời gian kết thúc (UTC ISO 8601).
      - `task`: Thông tin task.
        - `taskCode`: Mã task.
        - `aircraftId`: ID máy bay.
        - `minLevel`: Cấp độ tối thiểu yêu cầu.
  - `droppedTasks`: Danh sách các task bị hủy theo máy bay.
    - `aircraftId`: ID máy bay.
    - `tasks`: Danh sách task bị hủy.
      - `taskCode`: Mã task.
      - `aircraftId`: ID máy bay.
      - `minLevel`: Cấp độ tối thiểu yêu cầu.
