# Phân tích nguyên nhân Dropped Tasks & Đề xuất giải pháp

## 1. Tóm tắt vấn đề
- **Hiện tượng:** Thuật toán trả về khoảng 20-25 tasks bị dropped (không thể gán).
- **Đối tượng ảnh hưởng chính:** Nhân viên vệ sinh (CLEANER) và nhân viên bốc xếp (GROUND_HANDLING).

## 2. Nguyên nhân gốc rễ (Root Causes)

Sau khi thực hiện phân tích sâu (Deep Dive Analysis), chúng tôi đã xác định được 2 nguyên nhân chính:

### Nguyên nhân 1: Thiếu dữ liệu khoảng cách (Đã khắc phục)
- **Mô tả:** Ma trận khoảng cách (`distanceMatrix`) thiếu dữ liệu từ `HUB_01` tới hầu hết các Gate.
- **Hệ quả:** Thời gian di chuyển được tính là vô cực (`inf`), khiến Cleaners không thể di chuyển từ Hub đến vị trí làm việc.
- **Trạng thái:** Đã được fix bằng script `patch_input.py`.

### Nguyên nhân 2: Xung đột ràng buộc thời gian (Critical Path Constraint)
- **Mô tả:** Tổng thời gian thực hiện chuỗi công việc bắt buộc vượt quá thời gian máy bay đậu (Turnaround Time).
- **Chi tiết:**
  - Thời gian máy bay đậu (Time Window): **180 phút** (3 tiếng).
  - Chuỗi công việc bắt buộc (Critical Path):
    1. ARR-M: 25 phút
    2. UNLOAD: 40 phút
    3. CLEAN: 35 phút
    4. FUEL: 25 phút
    5. LOAD: 40 phút
    6. DEP-M: 25 phút
    -> **Tổng cộng: 190 phút.**
- **Kết luận:** Mỗi máy bay thiếu **10 phút** để hoàn thành quy trình. Điều này dẫn đến việc Solver buộc phải drop ít nhất 1 task trong chuỗi để thỏa mãn ràng buộc thời gian.

## 3. Giải pháp đề xuất

Để giải quyết vấn đề Critical Path Constraint, chúng tôi đề xuất chiến lược: **Song song hóa quy trình**.

### Chiến lược: Cho phép CLEAN và FUEL chạy song song
- **Thay đổi:** Loại bỏ sự phụ thuộc của task `FUEL` vào task `CLEAN`.
- **Tác động:**
  - Quy trình mới: `ARR-M -> UNLOAD -> {CLEAN, FUEL} -> LOAD -> DEP-M`
  - Thời gian Critical Path mới: 
    - Nhánh 1: ARR-M -> UNLOAD -> CLEAN -> LOAD -> DEP-M = 25 + 40 + 35 + 40 + 25 = 165 phút.
    - Nhánh 2: ARR-M -> UNLOAD -> FUEL -> LOAD -> DEP-M = 25 + 40 + 25 + 40 + 25 = 155 phút.
    -> **Max Path: 165 phút.**
- **Kết quả:** `165 phút < 180 phút` (Thỏa mãn). Dư ra 15 phút đệm cho mỗi máy bay.

## 4. Kế hoạch thực hiện
1. Modify file `input_complex_v2.json`: Cập nhật danh sách `dependencies` của task `FUEL`, loại bỏ `CLEAN` ra khỏi danh sách phụ thuộc.
2. Chạy lại thuật toán solver.
3. Verify kết quả: Đảm bảo số lượng Dropped Tasks giảm về 0.
