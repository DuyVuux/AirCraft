# 📖 User Guide

Hướng dẫn sử dụng hệ thống Aircraft Web.

## 🎯 Tổng quan

Hệ thống Aircraft Web cho phép bạn nhập dữ liệu cho hệ thống lập lịch nhân sự mặt đất tại sân bay bằng 2 cách:
1. **Upload file CSV/Excel**
2. **Nhập tay qua form**

## 📤 Upload File

### Bước 1: Tải Template

1. Chọn loại file bạn muốn upload (Employees, Aircrafts, Hubs, Time Matrix, Distance Matrix)
2. Nhấn nút **"Download Template"**
3. Mở file template và điền dữ liệu

### Bước 2: Upload File

1. Nhấn nút **"Choose File"** hoặc kéo thả file vào vùng upload
2. Hệ thống sẽ tự động validate file
3. Nếu có lỗi, hệ thống sẽ hiển thị thông báo lỗi
4. Nếu thành công, bạn sẽ thấy preview dữ liệu

### Bước 3: Xác nhận

1. Kiểm tra preview dữ liệu
2. Nhấn nút **"Confirm"** để lưu dữ liệu
3. Dữ liệu sẽ được thêm vào hệ thống

## ✍️ Nhập tay

### Quản lý Roles & Tasks

1. Vào menu **"Manual Input"** → **"Roles & Tasks Editor"**
2. **Thêm Role:**
   - Nhấn nút **"Add Role"**
   - Nhập tên role (ví dụ: MECHANIC)
   - Nhấn **"Save"**
3. **Thêm Task:**
   - Nhấn nút **"Add Task"**
   - Nhập taskCode (ví dụ: TASK_TIRE_CHECK)
   - Nhập description
   - Nhấn **"Save"**
4. **Map Role với Task:**
   - Chọn role từ dropdown
   - Chọn task từ checklist
   - Nhấn **"Save Mapping"**

### Quản lý Aircraft

1. Vào menu **"Manual Input"** → **"Aircraft Editor"**
2. **Thêm Aircraft:**
   - Nhấn nút **"Add Aircraft"**
   - Điền thông tin:
     - Aircraft ID (ví dụ: VN-A320)
     - Aircraft Type (dropdown: A320, B737, B787...)
     - Location (ví dụ: GATE-01)
     - GPS Coordinates (có thể auto-fill từ location)
     - Time Window (start và end time)
     - Required Tasks (multi-select)
   - Nhấn **"Save"**
3. **Sửa/Xóa Aircraft:**
   - Chọn aircraft từ danh sách
   - Nhấn **"Edit"** hoặc **"Delete"**

### Quản lý Hubs

1. Vào menu **"Manual Input"** → **"Hub Management"**
2. **Thêm Hub:**
   - Nhấn nút **"Add Hub"**
   - Điền thông tin:
     - Hub ID (ví dụ: HUB_01)
     - Location (ví dụ: REST_AREA_A)
     - GPS Coordinates
   - Nhấn **"Save"**

### Quản lý Employees

1. Vào menu **"Manual Input"** → **"Employee Management"**
2. **Thêm Employee:**
   - Nhấn nút **"Add Employee"**
   - Điền thông tin:
     - Employee ID (ví dụ: EMP_001)
     - Role (dropdown)
     - Level (dropdown: 1, 2, 3)
     - Working Times:
       - Nhấn **"Add Working Time"**
       - Chọn start time và end time
     - Break Times:
       - Nhấn **"Add Break Time"**
       - Chọn start time và end time (HH:MM)
   - Nhấn **"Save"**

### Quản lý Time Matrix

1. Vào menu **"Manual Input"** → **"Time Matrix Editor"**
2. **Thêm Entry:**
   - Chọn Task Code từ dropdown
   - Chọn Role từ dropdown
   - Nhập Level ID (1, 2, 3...)
   - Nhập Time Process (phút)
   - Nhấn **"Save"**

### Quản lý Distance Matrix

1. Vào menu **"Manual Input"** → **"Distance Matrix Editor"**
2. **Thêm Entry:**
   - Chọn Source location từ dropdown
   - Chọn Destination location từ dropdown
   - Nhập Value (km)
   - Nhấn **"Save"**
3. **Auto-generate:**
   - Nhấn nút **"Auto-generate"**
   - Hệ thống sẽ tự động tính khoảng cách dựa trên GPS coordinates

## 🔧 Developer Mode

### Sử dụng JSON Editor

1. Vào menu **"Developer Mode"**
2. **Nhập JSON:**
   - Dán JSON vào textarea
   - Hoặc upload file `.json`
3. **Validate:**
   - Nhấn nút **"Validate JSON"**
   - Hệ thống sẽ kiểm tra schema và hiển thị lỗi nếu có
4. **Load vào Form:**
   - Nhấn nút **"Load into Form"**
   - Dữ liệu sẽ được load vào các form tương ứng
5. **Export:**
   - Nhấn nút **"Export JSON"**
   - Tải file JSON về máy

## ✅ Validation Rules

### Employees
- employeeId phải unique
- role phải hợp lệ (MECHANIC, CLEANER, BAGGAGE_HANDLER, REFUEL_TECHNICIAN, GATE_AGENT, PUSHBACK_OPERATOR, CATERING_STAFF)
- level phải là 1, 2, hoặc 3
- workingTime_start < workingTime_end
- breakTime_start < breakTime_end

### Aircrafts
- aircraftId phải unique
- aType_id phải hợp lệ (A320, B737, B787, A350, B777, A380)
- timeWindow_start < timeWindow_end
- requiredTasks phải có trong timeMatrix

### Hubs
- hubId phải unique
- GPS coordinates hợp lệ (longitude: -180 đến 180, latitude: -90 đến 90)

### Time Matrix
- taskCode phải hợp lệ
- role phải hợp lệ
- levelId phải là số nguyên dương
- timeProcess phải > 0

### Distance Matrix
- source và destination phải tồn tại trong locations
- value phải >= 0

## 🆘 Troubleshooting

### Lỗi: "File format không hợp lệ"
**Giải pháp:** Đảm bảo file là CSV hoặc Excel (.xlsx)

### Lỗi: "Thiếu cột bắt buộc"
**Giải pháp:** Tải template và kiểm tra các cột bắt buộc

### Lỗi: "ID đã tồn tại"
**Giải pháp:** Sử dụng ID khác hoặc xóa entry cũ

### Lỗi: "Thời gian không hợp lệ"
**Giải pháp:** Kiểm tra format thời gian (ISO 8601 với 'Z' cho workingTime, HH:MM cho breakTime)

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng liên hệ:
- Email: support@example.com
- Hotline: 0123-456-789

