# ✈️ Hệ Thống Lập Lịch Nhân Viên Mặt Đất Sân Bay

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)

Ứng dụng web full-stack hiện đại để quản lý và nhập liệu dữ liệu lập lịch cho hoạt động nhân viên mặt đất sân bay. Hệ thống hỗ trợ nhập dữ liệu hiệu quả qua upload file CSV/Excel, form tương tác, và trình soạn thảo JSON dành cho developer.

---

## 📑 Mục Lục

- [Tổng Quan Dự Án](#-tổng-quan-dự-án)
- [Tính Năng](#-tính-năng)
- [Cấu Trúc Dự Án](#-cấu-trúc-dự-án)
- [Cài Đặt](#-cài-đặt)
- [Cấu Hình](#-cấu-hình)
- [Hướng Dẫn Sử Dụng](#-hướng-dẫn-sử-dụng)
- [Môi Trường & Yêu Cầu](#-môi-trường--yêu-cầu)
- [Hướng Dẫn Phát Triển & Đóng Góp](#-hướng-dẫn-phát-triển--đóng-góp)
- [Kiểm Thử](#-kiểm-thử)
- [Triển Khai](#-triển-khai)
- [Bảo Mật / Best Practices](#-bảo-mật--best-practices)
- [Xử Lý Sự Cố](#-xử-lý-sự-cố)
- [Lộ Trình Phát Triển](#-lộ-trình-phát-triển)
- [Giấy Phép](#-giấy-phép)

---

## 🎯 Tổng Quan Dự Án

**Hệ Thống Lập Lịch Nhân Viên Mặt Đất Sân Bay** được thiết kế để hỗ trợ nhập liệu cho việc lập lịch đội ngũ mặt đất sân bay. Hệ thống giải quyết các yêu cầu phức tạp trong việc quản lý:

- **Máy Bay (Aircrafts)** - Loại máy bay, vị trí, khung thời gian và các task bảo trì cần thiết
- **Nhân Viên (Employees)** - Đội ngũ mặt đất với vai trò, cấp độ, thời gian làm việc và lịch nghỉ
- **Hub** - Khu nghỉ ngơi và vị trí trung tâm cho nhân viên
- **Tuyến Xe Buýt & Trạm Dừng** - Logistics vận chuyển nội bộ sân bay
- **Ma Trận Khoảng Cách/Thời Gian** - Thời gian di chuyển và thời gian xử lý task

### Đối Tượng Sử Dụng

- Quản lý Vận hành Sân bay
- Nhân viên Lập lịch Đội ngũ Mặt đất
- Nhân viên Nhập liệu
- Developer và Tích hợp Hệ thống

### Công Nghệ Sử Dụng

| Tầng | Công Nghệ |
|------|-----------|
| **Frontend** | React 18, TypeScript, Vite, Material-UI (MUI) |
| **Backend** | FastAPI, Pydantic, Uvicorn |
| **Xử Lý Dữ Liệu** | Pandas, PapaParse, XLSX |
| **Bản Đồ & Trực Quan** | React Leaflet, Turf.js |
| **Code Editor** | Monaco Editor |
| **Validation Form** | Zod, React Hook Form |

---

## ✨ Tính Năng

### Phương Thức Nhập Liệu

- **📤 Upload File** - Hỗ trợ file CSV và Excel (.xlsx) với validation tự động
- **✍️ Nhập Thủ Công** - Form tương tác cho từng loại dữ liệu
- **🔧 Chế Độ Developer** - Trình soạn thảo JSON với syntax highlighting và schema validation

### Chức Năng Chính

| Tính Năng | Mô Tả |
|-----------|-------|
| **Quản Lý Template** | Tải template được cấu hình sẵn cho nhập liệu |
| **Validation Thời Gian Thực** | Phản hồi ngay lập tức về chất lượng và định dạng dữ liệu |
| **Xem Trước Dữ Liệu** | Xem trước trực quan trước khi gửi |
| **Trực Quan Bản Đồ** | Bản đồ tương tác cho quản lý tọa độ GPS |
| **Theo Dõi Lịch Sử** | Theo dõi và quản lý các dataset đã gửi |
| **Xuất Đa Định Dạng** | Xuất dữ liệu dạng JSON, CSV, hoặc Excel |

### Các Component Editor

- **Roles & Tasks Editor** - Định nghĩa vai trò nhân viên và ánh xạ task
- **Aircraft Editor** - Quản lý đội máy bay và các task cần thiết
- **Hub Management** - Cấu hình khu nghỉ ngơi và hub nhân viên
- **Employee Management** - Hồ sơ nhân viên với lịch làm việc
- **Time Matrix Editor** - Thời gian xử lý task theo vai trò và cấp độ
- **Distance Matrix Editor** - Thời gian di chuyển giữa các vị trí

---

## 📁 Cấu Trúc Dự Án

```
AirCraft/
├── backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/        # Các endpoint API
│   │   │       ├── upload.py      # Xử lý upload file
│   │   │       ├── validate.py    # Validation dữ liệu
│   │   │       ├── templates.py   # Quản lý template
│   │   │       ├── submit.py      # Gửi dữ liệu
│   │   │       ├── datasets.py    # Thao tác dataset
│   │   │       ├── airports.py    # Dữ liệu sân bay
│   │   │       └── map.py         # Thao tác bản đồ/GIS
│   │   └── services/          # Business logic
│   ├── data/                  # File dữ liệu lưu trữ
│   ├── main.py               # Entry point FastAPI
│   └── requirements.txt      # Dependencies Python
│
├── frontend/                  # Frontend React
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── common/          # UI components dùng chung
│   │   │   ├── developer/       # Components JSON editor
│   │   │   ├── editor/          # Form chỉnh sửa dữ liệu
│   │   │   ├── layout/          # Components layout
│   │   │   ├── scheduler/       # Giao diện lập lịch
│   │   │   ├── tabs/            # Components tab
│   │   │   └── upload/          # Components upload file
│   │   ├── contexts/         # React Context providers
│   │   ├── hooks/            # Custom React hooks
│   │   ├── pages/            # Page components
│   │   │   ├── HomePage.tsx
│   │   │   ├── DeveloperPage.tsx
│   │   │   ├── ManualInputPage.tsx
│   │   │   ├── MapEditorPage.tsx
│   │   │   ├── HistoryPage.tsx
│   │   │   ├── ProductPage.tsx
│   │   │   └── SchedulerPage.tsx
│   │   ├── services/         # Tầng service API
│   │   ├── types/            # Định nghĩa TypeScript
│   │   ├── utils/            # Hàm tiện ích
│   │   └── styles/           # Styles toàn cục
│   ├── package.json
│   └── vite.config.ts
│
├── docs/                      # Tài liệu
│   ├── USER_GUIDE.md
│   └── DEVELOPMENT_GUIDE.md
│
├── sample/                    # File dữ liệu mẫu
│   ├── input_sample.json         # Ví dụ input hoàn chỉnh
│   ├── output_sample.json        # Định dạng output mong đợi
│   ├── flights.csv
│   ├── employees.csv
│   └── tasks.csv
│
├── templates/                 # Template CSV
│   ├── aircrafts_template.csv
│   ├── employees_template.csv
│   ├── hubs_template.csv
│   ├── time_matrix_template.csv
│   ├── distance_matrix_template.csv
│   ├── bus_routes_template.csv
│   └── bus_stops_template.csv
│
├── start-all.sh              # Script khởi động Linux/Mac
├── start-all.bat             # Script khởi động Windows
├── requirements.txt          # Dependencies Python gốc
└── README.md
```

---

## 🚀 Cài Đặt

### Yêu Cầu Trước

- **Node.js** 18.0 trở lên
- **npm** 9.0+ hoặc **yarn** 1.22+
- **Python** 3.9 trở lên
- **Git**

### Khởi Động Nhanh

#### 1. Clone Repository

```bash
git clone <repository-url>
cd AirCraft
```

#### 2. Cài Đặt Backend

```bash
cd backend

# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
# Linux/Mac:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt
```

#### 3. Cài Đặt Frontend

```bash
cd frontend

# Cài đặt dependencies
npm install
```

#### 4. Khởi Động Ứng Dụng

**Cách A: Sử dụng script khởi động**

```bash
# Linux/Mac
chmod +x start-all.sh
./start-all.sh

# Windows
start-all.bat
```

**Cách B: Khởi động thủ công**

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate  # hoặc .\venv\Scripts\activate trên Windows
uvicorn main:app --reload --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

#### 5. Truy Cập Ứng Dụng

- **Frontend**: http://localhost:5173 (hoặc http://localhost:3000)
- **Backend API**: http://localhost:8000
- **Tài Liệu API**: http://localhost:8000/docs

---

## ⚙️ Cấu Hình

### Cấu Hình Backend

Backend sử dụng FastAPI với các cài đặt mặc định sau:

| Cài Đặt | Mặc Định | Mô Tả |
|---------|----------|-------|
| Host | `0.0.0.0` | Địa chỉ bind server |
| Port | `8000` | Port server |
| Reload | `true` | Tự động reload khi có thay đổi |
| CORS Origins | `localhost:3000`, `localhost:5173` | Các origin frontend được phép |

### Cấu Hình Frontend

Chỉnh sửa `frontend/vite.config.ts` cho cài đặt tùy chỉnh:

```typescript
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```

### Biến Môi Trường

Tạo file `.env` cho cấu hình theo môi trường:

```bash
# backend/.env
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# frontend/.env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📖 Hướng Dẫn Sử Dụng

### Quy Trình Upload File

1. **Tải Template** - Chọn loại dữ liệu và tải template CSV
2. **Điền Dữ Liệu** - Nhập dữ liệu theo định dạng template
3. **Upload File** - Kéo thả hoặc chọn file
4. **Validate** - Hệ thống tự động validate dữ liệu
5. **Xem Trước** - Xem lại dữ liệu đã parse
6. **Xác Nhận** - Gửi để lưu dữ liệu

### Nhập Thủ Công

Truy cập **Manual Input** để sử dụng các editor cho:

- Ánh Xạ Roles & Tasks
- Quản Lý Đội Máy Bay
- Cấu Hình Hub
- Hồ Sơ Nhân Viên
- Ma Trận Thời Gian/Khoảng Cách

### Chế Độ Developer (JSON Editor)

Truy cập **Developer Mode** để:

- Paste hoặc upload dữ liệu JSON
- Chỉnh sửa với Monaco Editor (đầy đủ tính năng IDE)
- Validate theo schema
- Load dữ liệu vào form
- Xuất file JSON

### Cấu Trúc JSON Mẫu

```json
{
  "trackingId": "PLAN-2024-12-05-001",
  "aircrafts": [
    {
      "aircraftId": "VN-A320",
      "aType": { "id": "A320", "desc": "Airbus A320" },
      "location": {
        "locationId": "GATE-01",
        "locationType": "GATE",
        "longitude": 106.6588,
        "latitude": 10.8185
      },
      "timeWindow": {
        "start": "2024-12-05T08:00:00Z",
        "end": "2024-12-07T12:00:00Z"
      },
      "requiredTasks": [
        { "taskCode": "TASK_TIRE_CHECK", "minLevel": 1 }
      ]
    }
  ],
  "employees": [...],
  "hubs": [...],
  "busStops": [...],
  "busRoutes": [...],
  "matrixConfigs": {
    "distanceMatrix": [...],
    "timeMatrix": [...],
    "busTransitMatrix": [...],
    "walkingDistanceFromLocationToBusStop": [...]
  }
}
```

---

## 💻 Môi Trường & Yêu Cầu

### Yêu Cầu Backend

| Package | Phiên Bản | Mục Đích |
|---------|-----------|----------|
| fastapi | 0.104.1 | Web framework |
| uvicorn | 0.24.0 | ASGI server |
| pydantic | 2.5.0 | Validation dữ liệu |
| pandas | 2.1.3 | Xử lý dữ liệu |
| python-multipart | 0.0.6 | Upload file |
| openpyxl | 3.1.2 | Xử lý file Excel |
| python-dateutil | 2.8.2 | Parse ngày tháng |

### Yêu Cầu Frontend

| Package | Phiên Bản | Mục Đích |
|---------|-----------|----------|
| react | 18.2.x | UI framework |
| typescript | 5.2.x | Type safety |
| vite | 5.0.x | Build tool |
| @mui/material | 5.14.x | UI components |
| react-leaflet | 4.2.x | Trực quan bản đồ |
| @monaco-editor/react | 4.7.x | Code editor |
| zod | 3.22.x | Schema validation |
| react-hook-form | 7.48.x | Quản lý form |

---

## 🤝 Hướng Dẫn Phát Triển & Đóng Góp

### Tiêu Chuẩn Code

- **TypeScript**: Bật strict mode, không dùng type `any`
- **React**: Functional components với hooks
- **Python**: Tuân thủ PEP 8, sử dụng type hints

### Quy Ước Đặt Tên

| Loại | Quy Ước | Ví Dụ |
|------|---------|-------|
| Components | PascalCase | `AircraftEditor.tsx` |
| Hooks | camelCase + tiền tố `use` | `useEmployeeData.ts` |
| Utils | camelCase | `formatDate.ts` |
| API Routes | snake_case | `upload_file` |

### Quy Trình Đóng Góp

1. Fork repository
2. Tạo nhánh feature (`git checkout -b feature/tinh-nang-moi`)
3. Thực hiện thay đổi theo tiêu chuẩn code
4. Viết hoặc cập nhật tests
5. Commit với message rõ ràng (`git commit -m 'feat: thêm tính năng mới'`)
6. Push lên nhánh (`git push origin feature/tinh-nang-moi`)
7. Mở Pull Request

### Định Dạng Commit Message

```
<type>: <mô tả>

[nội dung tùy chọn]

Các type: feat, fix, docs, style, refactor, test, chore
```

---

## 🧪 Kiểm Thử

### Tests Backend

```bash
cd backend
python -m pytest

# Với coverage
python -m pytest --cov=app
```

### Tests Frontend

```bash
cd frontend

# Unit tests
npm run test

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e
```

### Kiểm Tra API

```bash
# Validate endpoint upload
python backend/test_upload_data.py

# Validate cấu trúc
python backend/validate_structure.py
```

---

## 🚀 Triển Khai

### Build Production

#### Frontend

```bash
cd frontend
npm run build
# Output: frontend/dist/
```

#### Backend

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Triển Khai Docker

```dockerfile
# Dockerfile.backend
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Stack Production Khuyến Nghị

- **Reverse Proxy**: Nginx
- **Process Manager**: PM2 (frontend), Gunicorn (backend)
- **Container**: Docker + Docker Compose
- **CI/CD**: GitHub Actions / GitLab CI

---

## 🔒 Bảo Mật / Best Practices

### Validation Input

- Tất cả file upload được validate về loại và kích thước
- JSON schema validation sử dụng Pydantic và Zod
- Làm sạch dữ liệu CSV/Excel trước khi xử lý

### Bảo Mật API

- CORS được cấu hình chỉ cho các origin cụ thể
- Làm sạch input trên tất cả endpoints
- Khuyến nghị rate limiting cho production

### Xử Lý Dữ Liệu

- Tọa độ GPS được validate trong phạm vi hợp lệ
- Định dạng thời gian tuân thủ chuẩn ISO 8601
- ID phải là duy nhất trong từng category

### Khuyến Nghị

- [ ] Bật HTTPS trong production
- [ ] Triển khai xác thực (JWT/OAuth)
- [ ] Thêm rate limiting cho request
- [ ] Cấu hình logging phù hợp
- [ ] Thiết lập monitoring và alerts

---

## ❓ Xử Lý Sự Cố

### Các Lỗi Thường Gặp

| Lỗi | Nguyên Nhân | Giải Pháp |
|-----|-------------|-----------|
| Định dạng file không hợp lệ | Sai phần mở rộng file | Chỉ sử dụng file CSV (.csv) hoặc Excel (.xlsx) |
| Thiếu cột bắt buộc | Không khớp template | Tải và sử dụng template mới nhất |
| ID đã tồn tại | Entry trùng lặp | Sử dụng ID duy nhất hoặc xóa entry cũ |
| Định dạng thời gian không hợp lệ | Sai format | Sử dụng ISO 8601 (vd: `2024-12-05T08:00:00Z`) |
| Tọa độ GPS không hợp lệ | Ngoài phạm vi | Longitude: -180 đến 180, Latitude: -90 đến 90 |
| Lỗi CORS | Origin không được phép | Thêm URL frontend vào CORS origins của backend |
| JSON validation thất bại | Không khớp schema | Kiểm tra `src/utils/jsonValidator.ts` để xem schema |

### Mẹo Debug

- **Frontend**: Sử dụng React DevTools và console trình duyệt
- **Backend**: Kiểm tra logs auto-reload của FastAPI
- **Vấn đề API**: Test endpoints tại http://localhost:8000/docs

---

## 🛣️ Lộ Trình Phát Triển

- [ ] **v1.1** - Xác thực và phân quyền người dùng
- [ ] **v1.2** - Chỉnh sửa cộng tác thời gian thực
- [ ] **v1.3** - Tích hợp thuật toán lập lịch
- [ ] **v2.0** - Hỗ trợ đa sân bay
- [ ] **v2.1** - Giao diện tương thích mobile
- [ ] **v2.2** - Báo cáo và phân tích nâng cao
- [ ] **v3.0** - Machine learning cho tối ưu lịch trình

---

## 📄 Giấy Phép

Dự án này được cấp phép theo Giấy phép MIT. Xem file [LICENSE](LICENSE) để biết chi tiết.

---

## 📞 Hỗ Trợ

Để được hỗ trợ, vui lòng liên hệ:

- **Email**: support@example.com
- **Tài liệu**: [Hướng Dẫn Sử Dụng](docs/USER_GUIDE.md) | [Hướng Dẫn Phát Triển](docs/DEVELOPMENT_GUIDE.md)

---

<p align="center">
  Xây dựng với ❤️ cho hoạt động sân bay hiệu quả
</p>
