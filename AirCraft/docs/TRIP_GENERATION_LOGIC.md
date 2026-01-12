# Trip Generation Logic - Technical Documentation

> **Version**: v1.0  
> **Last Updated**: 2026-01-06  
> **Status**: Implemented & Verified

---

## 1. Mục tiêu

Hệ thống Trip Generation được thiết kế để **pre-calculate** các lộ trình di chuyển hợp lệ (Trips) giữa các điểm trên bản đồ sân bay. Mỗi Trip đại diện cho một đường đi ngắn nhất giữa hai điểm, được tính toán bằng thuật toán **Floyd-Warshall**.

### 1.1 Yêu cầu nghiệp vụ

- Phân biệt **phương thức di chuyển** (Walk vs Bus) dựa trên khoảng cách
- Hỗ trợ **ngưỡng đi bộ** (`epsilon_walk`) có thể cấu hình từ UI
- Không phá vỡ kiến trúc hiện tại (chỉ thay đổi business logic layer)
- Gắn **metadata tags** để truy vết nguồn gốc của mỗi Trip

---

## 2. Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
├─────────────────────────────────────────────────────────────────┤
│  MapEditorTab.tsx                                               │
│    ├── Input: epsilon_walk (Ngưỡng đi bộ)                       │
│    └── Render: Dashed line (WALK) / Solid line (BUS)            │
│                                                                 │
│  GlobalDataContext.tsx                                          │
│    ├── State: epsilonWalk, mapTrips                             │
│    └── API Call: POST /api/map/generate-trips                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          BACKEND                                │
├─────────────────────────────────────────────────────────────────┤
│  api/routes/map.py                                              │
│    └── POST /generate-trips                                     │
│         ├── Input: nodes, edges, epsilon_walk                   │
│         └── Output: trips[], cacheKey                           │
│                                                                 │
│  services/trip_generator.py                                     │
│    └── generate_trips(nodes, edges, epsilon_walk)               │
│         ├── Rule 1: Stand ↔ Stand                               │
│         ├── Rule 2: Bus Stop → Stand                            │
│         ├── Rule 3: Rest Area → Bus Stop                        │
│         └── Rule 4: Rest Area → Stand                           │
│                                                                 │
│  services/graph_service.py                                      │
│    └── Floyd-Warshall (Numba accelerated)                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Trip Schema (v1)

```typescript
interface MapTrip {
  id: string           // "trip_{fromId}_to_{toId}"
  name: string         // "Stand 1 → Stand 2"
  color: string        // Hex color for visualization
  edgeIds: string[]    // List of edge IDs forming the path
  distance: number     // Total distance in meters
  path: string[]       // List of node IDs (ordered)
  mode: 'WALK' | 'BUS' // Transportation mode
  tags: string[]       // Metadata tags for debugging
}
```

### 3.1 Mode Types

| Mode | Mô tả | Hiển thị UI |
|------|-------|-------------|
| `WALK` | Di chuyển bằng đi bộ | Nét đứt (dashed) |
| `BUS` | Di chuyển bằng xe bus | Nét liền (solid) |

### 3.2 Tags Reference

| Tag | Ý nghĩa |
|-----|---------|
| `stand_transfer` | Trip giữa 2 aircraft stands |
| `proximity_walk` | Đi bộ do khoảng cách ≤ epsilon |
| `distance_heuristic_bus` | Bus do khoảng cách > epsilon (heuristic) |
| `bus_route` | Trip từ Bus Stop đến Stand |
| `depot_exit` | Trip từ Rest Area đến Bus Stop (xe rời bãi) |
| `direct_walk` | Đi bộ trực tiếp từ Rest Area đến Stand |

---

## 4. Business Rules

### Rule 1: Stand ↔ Stand (Bidirectional)

```
Điều kiện: Cả 2 đầu đều là aircraft_stand
Logic:
  - Nếu distance ≤ epsilon_walk → Mode: WALK
  - Nếu distance > epsilon_walk → Mode: BUS
Tags: ['stand_transfer', 'proximity_walk' | 'distance_heuristic_bus']
```

### Rule 2: Bus Stop → Stand (One-way)

```
Điều kiện: From = bus_stop, To = aircraft_stand
Logic: Luôn là BUS (xe bus chở nhân viên đến stand)
Tags: ['bus_route']
```

### Rule 3: Rest Area → Bus Stop (One-way)

```
Điều kiện: From = rest_area, To = bus_stop
Logic: Luôn là BUS (xe rời khỏi bãi đỗ)
Tags: ['depot_exit']
```

### Rule 4: Rest Area → Stand (One-way, Conditional)

```
Điều kiện: From = rest_area, To = aircraft_stand
Logic:
  - Nếu distance ≤ epsilon_walk → Mode: WALK, Trip được tạo
  - Nếu distance > epsilon_walk → KHÔNG tạo Trip
Tags: ['direct_walk']
```

---

## 5. Node Types

| Type | Vai trò | Có thể là Start/End? |
|------|---------|---------------------|
| `aircraft_stand` | Vị trí đỗ máy bay | ✅ Có |
| `bus_stop` | Điểm dừng xe bus | ✅ Có |
| `rest_area` | Khu nghỉ / bãi xe | ✅ Có |
| `direction` | Node trung gian dẫn đường | ❌ Không (chỉ trong path) |

---

## 6. API Reference

### POST `/api/map/generate-trips`

**Request Body:**

```json
{
  "airportId": "noi-bai",
  "nodes": [...],
  "edges": [...],
  "cachedHash": "abc123",
  "epsilon_walk": 50.0
}
```

**Response:**

```json
{
  "cached": false,
  "cacheKey": "def456",
  "trips": [
    {
      "id": "trip_stand1_to_stand2",
      "name": "Stand 1 → Stand 2",
      "color": "#3B82F6",
      "edgeIds": ["edge1", "edge2"],
      "distance": 45.5,
      "path": ["stand1", "dir1", "stand2"],
      "mode": "WALK",
      "tags": ["stand_transfer", "proximity_walk"]
    }
  ]
}
```

---

## 7. Files liên quan

### Backend

| File | Mô tả |
|------|-------|
| `backend/app/api/routes/map.py` | API endpoint `/generate-trips` |
| `backend/app/services/trip_generator.py` | Core logic sinh trips |
| `backend/app/services/graph_service.py` | Floyd-Warshall wrapper |
| `backend/app/services/floyd_warshall.py` | Numba-accelerated algorithm |

### Frontend

| File | Mô tả |
|------|-------|
| `frontend/src/types/mapEditor.ts` | TypeScript types cho MapTrip |
| `frontend/src/contexts/GlobalDataContext.tsx` | State management & API calls |
| `frontend/src/components/editor/MapEditorTab.tsx` | UI hiển thị trips |

---

## 8. Giả định & Hạn chế (v1)

### 8.1 Các giả định hiện tại

1. **Distance Heuristic**: Mọi di chuyển Stand-to-Stand xa (> epsilon) đều mặc định là BUS. Đây là simplification, được flag bằng tag `distance_heuristic_bus`.

2. **Depot Exit**: Mọi di chuyển từ Rest Area ra Bus Stop đều là phương tiện cơ giới (BUS mode), không phân biệt khoảng cách.

3. **No Mixed Mode**: Một Trip chỉ có 1 mode duy nhất (hoàn toàn WALK hoặc hoàn toàn BUS).

4. **Undirected Walking**: Đi bộ được coi là undirected (có thể đi 2 chiều với cùng distance).

### 8.2 Hạn chế cần lưu ý

- Chưa hỗ trợ **time-dependent routing** (giờ cao điểm)
- Chưa phân biệt **nhiều loại nhân viên** (role-based routing)
- Chưa có khái niệm **vùng cấm** (restricted zones)
- Bus route chưa theo đường thực tế (teleport model)

---

## 9. Hướng phát triển tương lai

> ⚠️ **Các hướng dưới đây là định hướng, chưa đủ dữ liệu để triển khai**

1. **Policy Configuration**: Cho phép admin cấu hình rules (không hard-code)
2. **Multi-mode Trips**: Một trip có thể kết hợp WALK + BUS
3. **Real Bus Routes**: Model đường bus thực tế thay vì teleport
4. **Role-based Routing**: Khác nhau theo loại nhân viên
5. **Time Windows**: Xét giờ cao điểm / giờ thấp điểm

---

## 10. Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-01-06 | Initial release with Walk/Bus modes, epsilon parameter, and metadata tags |

