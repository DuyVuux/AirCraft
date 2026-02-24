# ✈️ Ứng Dụng AirCraft (Backend & Frontend)

Thư mục này chứa toàn bộ hệ thống Web Application cốt lõi cho dự án AirCraft, đã được hợp nhất và hiện đại hóa.

## 🌐 Tổng Quan Giao Diện Hệ Thống

Hệ thống bao gồm một Frontend động sử dụng React/Vite kết hợp với Backend mạnh mẽ dựa trên FastAPI. Đợt "Hợp nhất Kiến trúc (Architecture Consolidation)" gần đây đã chuyển hoàn toàn chức năng lập lịch vào FastAPI, loại bỏ sự phụ thuộc vào ứng dụng Flask độc lập cũ. Backend hiện đảm nhận HTTP requests, xác thực, lưu trữ dữ liệu thông qua SQLAlchemy và xử lý bất đồng bộ các tác vụ thuật toán chuyên sâu trên CPU.

---

## ⚙️ Backend (FastAPI)

Được xây dựng để đáp ứng độ đồng thời cao, bảo mật mạnh mẽ và tối ưu trải nghiệm của lập trình viên.

### Các Tính Năng Cốt Lõi
- **Xác Thực JWT & Token Refresh**: Cơ chế đăng nhập cung cấp `access_token` có hiệu lực ngắn và `refresh_token` kéo dài 7 ngày (tại `/api/auth/refresh`). Yêu cầu secret keys cực kỳ nghiêm ngặt (>32 ký tự).
- **Phân Quyền Dựa Trên Vai Trò (RBAC)**: Được xử lý tự động thông qua decorator `require_role()`. Bảo vệ các API, đảm bảo chỉ những người dùng có quyền `Admin`, `Operator`, hoặc `Viewer` mới được phép thực hiện các thao tác thay đổi dữ liệu.
- **Bảo Mật Mặc Định**: Tích hợp cấu hình CORS được nạp từ biến môi trường (Environment Variables), hạn chế lượng truy cập bằng `slowapi` (VD: tối đa 5 lần đăng nhập/phút), và kiểm tra chặt chẽ payload đầu vào (giới hạn ở 10MB) để phòng chống tấn công DDoS.

### Cơ Sở Dữ Liệu & Migrations (Alembic)
Hệ thống đã loại bỏ việc đọc/ghi trực tiếp từ file JSON dễ bị lỗi, chuyển sang cấu trúc an toàn của **SQLAlchemy**. Các Entities chính bao gồm `Aircraft`, `Employee`, `MaintenanceTask`, và `ScheduleJob`. 

Mọi thay đổi trong lược đồ (Schema) đều được quản lý thông qua công cụ Migration **Alembic**.
```bash
# Để nâng cấp CSDL lên phiên bản schema mới nhất:
alembic upgrade head
```

### 🛣️ Các Tham Số API (Endpoints) Quan Trọng

| Method | Endpoint | Mô tả |
|:---:|---|---|
| POST | `/api/auth/login` | Xác thực người dùng và trả về chùm khóa JWT. |
| POST | `/api/auth/refresh` | Cấp lại `access_token` mới thông qua Refresh Token hiện có. |
| POST | `/api/scheduler/run` | Gửi yêu cầu giải quyết lịch trình. Endpoint lập tức trả về `job_id` trong khi `ProcessPoolExecutor` chạy nền để xử lý thuật toán LNS bất đồng bộ. |
| GET | `/api/scheduler/status/{job_id}` | Truy vấn trạng thái vòng đời của một Job (`PENDING` -> `RUNNING` -> `COMPLETED`/`FAILED`). |
| GET | `/api/scheduler/algorithms` | Lấy danh sách các thuật toán tối ưu hóa hiện có trên Server. |

---

## 🖥️ Frontend (React & Vite)

### Công Nghệ
- React 18 & TypeScript
- Trình biên dịch Vite
- HTTP Interceptors tiêu chuẩn tự động thiết lập Header `Authorization: Bearer <token>` trên mỗi Requests.

### Hướng Dẫn Khởi Chạy Frontend

Yêu cầu máy tính cài đặt sẵn `Node.js` (≥18).

```bash
cd frontend

# Cài đặt tất cả thư viện (tạo thư mục node_modules)
npm install

# Bật máy chủ phát triển (HMR) 
npm run dev
```

Frontend này sẽ kết nối nội bộ với FastAPI Backend thường chạy tại cổng `8002`. Vui lòng luôn kiểm tra file `.env` của backend, xem xét mục `ALLOWED_ORIGINS` để thêm địa chỉ gốc của Frontend, nhằm vượt qua chính sách CORS an toàn.
