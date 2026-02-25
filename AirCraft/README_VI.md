# ✈️ AirCraft: Ứng Dụng Lõi & Giao Diện Người Dùng

Thư mục này chứa các tầng **Quản Lý Dữ Liệu** và **Giao Diện Người Dùng** cốt lõi cho Hệ thống Lập lịch Đội ngũ Nhân viên Sân bay AirCraft.

Nó được chia thành hai phân hệ chính:
1. `backend/`: Ứng dụng Python FastAPI xử lý đồng thời cực cao, chịu trách nhiệm kết nối Cơ sở dữ liệu và Xác thực người dùng.
2. `frontend/`: Ứng dụng React động được xây dựng bằng công cụ Vite và ngôn ngữ TypeScript.

---

## ⚙️ Backend (FastAPI)

Backend đóng vai trò là "người gác cổng" tập trung cho mọi thao tác thay đổi dữ liệu và xác thực của hệ thống.

### Tính Năng Chính
- **JWT & Phân Quyền Vai Trò (Roles)**: Cung cấp `access_token` và `refresh_token`. Các API sẽ được bảo vệ nghiêm ngặt qua decorator `require_role(["admin", "operator", "viewer"])`.
- **Toàn Vẹn Dữ Liệu Quan Hệ**: Sử dụng SQLAlchemy với CSDL `sqlite` (hoặc PostgreSQL ở môi trường production). Các cấu trúc bảng được kiểm soát chặt chẽ thông qua Alembic Migrations.
- **Bảo Mật Tăng Cường**: Tích hợp các biện pháp phòng vệ CORS cấu hình qua Biến Môi Trường, Giới hạn truy cập bằng `slowapi`, và Giới hạn dung lượng tải trọng (Payload Limits) để chặn DDoS.

### Hướng Dẫn Cài Đặt Local

```bash
cd backend

# Thiết lập Môi trường ảo (Virtual Environment)
python3 -m venv .venv
source .venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt

# Thiết lập Cấu hình Biến Môi Trường (.env)
cat <<EOF > .env
API_HOST=0.0.0.0
API_PORT=8002
JWT_SECRET_KEY=yoursecretkeythatisatleast32characterslong123
REFRESH_SECRET_KEY=yourrefreshsecretkeythatisatleast32chars123
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
DATABASE_URL=sqlite:///./aircraft.db
EOF

# Đảm bảo Cơ sở dữ liệu được cập nhật lên cấu trúc mới nhất
alembic upgrade head

# Khởi chạy Server
uvicorn main:app --env-file .env --reload --port 8002
```

Mở trình duyệt truy cập vào [http://localhost:8002/docs](http://localhost:8002/docs) để xem tài liệu API Swagger tích hợp sẵn.

---

## 🖥️ Frontend (React & Vite)

Frontend xử lý quá trình Validation theo thời gian thực, tải dữ liệu (CSV/Excel), tích hợp bản đồ, và hệ thống Dashboard cho tương tác trực quan.

### Hướng Dẫn Cài Đặt Local

Yêu cầu máy tính cài đặt sẵn **Node.js 18+**.

```bash
cd frontend

# Chỉ định cho Frontend biết vị trí của Backend FastAPI đang chạy
echo "VITE_API_BASE_URL=http://localhost:8002" > .env

# Tải và cài đặt các Modules cần thiết
npm install

# Khởi động máy chủ phát triển (Hỗ trợ nạp lại code nóng - HMR)
npm run dev
```

Truy cập [http://localhost:5173](http://localhost:5173) để mở Ứng dụng Web.

---

## 🧪 Kiểm Thử

Có thể chạy trực tiếp bộ công cụ Unit Test cho Backend bằng lệnh sau:
```bash
cd backend
pytest tests/
```
