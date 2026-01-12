# Aircraft Maintenance Scheduler

Hệ thống tối ưu lịch bảo trì máy bay sử dụng OR-Tools (CP-SAT + MIP).

## 📋 Mô tả

Giải quyết bài toán gán task bảo trì cho nhân viên với các ràng buộc:
- Thời gian làm việc của nhân viên
- Cửa sổ thời gian của máy bay
- Kỹ năng và level của nhân viên
- Thời gian di chuyển giữa các vị trí
- Precedence giữa các task

## 🚀 Cài đặt

### Yêu cầu
- Python 3.8+
- pip

### Cài đặt dependencies

```bash
pip install flask flask-cors ortools
```

Hoặc tạo file `requirements.txt`:
```
flask>=2.0.0
flask-cors>=3.0.0
ortools>=9.0.0
```

Và chạy:
```bash
pip install -r requirements.txt
```

## 🖥️ Chạy Server

### Khởi động server

```bash
python3 main.py
```

Server sẽ chạy tại:
- **Local**: http://127.0.0.1:8000
- **Network**: http://[your-ip]:8000

### Các trang web

| URL | Mô tả |
|-----|-------|
| http://127.0.0.1:8000 | Dashboard chính - xem solutions |
| http://127.0.0.1:8000/benchmark | Benchmark Dashboard - so sánh strategies |
| http://127.0.0.1:8000/visualize/{filename} | Visualize một solution cụ thể |

## 📁 Cấu trúc thư mục

```
aircraft/
├── main.py                 # Entry point - Flask server
├── solver.py               # Standalone solver script
├── data/
│   ├── input/             # Input JSON files
│   └── output/            # Output solutions
├── src/
│   ├── model/             # Data models
│   ├── strategy/          # Solver strategies
│   │   ├── orStrategy/    # CP-SAT solver
│   │   └── hybridStrategy/# Hybrid CP-SAT + MIP solver
│   ├── benchmark/         # Benchmarking tools
│   └── visualization/     # Web UI templates
└── docs/                   # Documentation
```

## 🔧 Solver Strategies

### 1. CP-SAT (OrStrategy)
- Pure OR-Tools CP-SAT solver
- Tìm solution tối ưu nhưng có thể chậm với instances lớn

### 2. Hybrid (HybridStrategy)
- **Phase 1**: CP-SAT tìm feasible assignments (80% time)
- **Phase 2**: MIP tối ưu thời gian bắt đầu (20% time)
- Thường nhanh hơn với instances lớn

## 📊 Chạy Benchmark

### Qua Web UI
1. Vào http://127.0.0.1:8000/benchmark
2. Chọn strategies (CP-SAT, Hybrid)
3. Chọn instance sizes hoặc Custom
4. Đặt time limit
5. Click "Run Benchmark"

### Qua API

```bash
curl -X POST http://127.0.0.1:8000/api/benchmark/run \
  -H "Content-Type: application/json" \
  -d '{
    "strategies": ["cpsat", "hybrid"],
    "sizes": ["small", "medium"],
    "time_limit": 30
  }'
```

### Custom Instance

```bash
curl -X POST http://127.0.0.1:8000/api/benchmark/run \
  -H "Content-Type: application/json" \
  -d '{
    "strategies": ["cpsat", "hybrid"],
    "custom_config": {
      "num_aircrafts": 10,
      "tasks_per_aircraft": 5,
      "num_employees": 20
    },
    "time_limit": 60
  }'
```

## 📝 API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/` | Dashboard chính |
| GET | `/benchmark` | Benchmark dashboard |
| GET | `/visualize/{filename}` | Visualize solution |
| GET | `/api/data/{filename}` | Lấy data của solution |
| GET | `/api/inputs` | List input files |
| POST | `/api/solve/{filename}` | Chạy solver trên input file |
| POST | `/api/benchmark/run` | Chạy benchmark |

### Solve Input File

```bash
curl -X POST "http://127.0.0.1:8000/api/solve/input_sample.json?strategy=hybrid&time_limit=30"
```

## ⚙️ Cấu hình

### Time Limit Options
- 10s, 30s, 60s, 120s, 5m, 10m
- Custom (1-3600 seconds)
- Unlimited (0)

### Instance Sizes
| Size | Aircrafts | Tasks | Employees |
|------|-----------|-------|-----------|
| Small | 3 | 9 | 5 |
| Medium | 10 | 50 | 20 |
| Large | 20 | 100 | 40 |

## 📈 Giải thích Status

| Status | Ý nghĩa |
|--------|---------|
| **OPTIMAL** | Đã chứng minh là tối ưu nhất |
| **FEASIBLE** | Tìm được lời giải nhưng chưa chứng minh tối ưu |
| **INFEASIBLE** | Không tìm được lời giải (constraints mâu thuẫn) |
| **UNKNOWN** | Không có thông tin optimality |

## 🛠️ Development

### Chạy tests
```bash
python -m pytest tests/
```

### Debug mode
Server mặc định chạy ở debug mode với hot reload.

## 📄 License

MIT License
