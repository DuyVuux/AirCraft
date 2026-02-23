# Input Data Description

**Generated:** 2026-01-21 12:36:00

**Tracking ID:** `PLAN-2024-12-05-001`

---

## Summary

| Entity | Count |
|--------|-------|
| Aircrafts | 2 |
| Hubs | 1 |
| Employees | 3 |
| Bus Stops | 3 |
| Bus Routes | 1 |

## Aircrafts

### VN-A320
- **Type:** Airbus A320 (`A320`)
- **Location:** GATE-01 (GATE)
  - Coordinates: (106.6588, 10.8185)
- **Time Window:** 2024-12-05T08:00:00Z → 2024-12-07T12:00:00Z
- **Required Tasks:** 2
  - `TASK_TIRE_CHECK` (required certs: CERT_BASIC_MAINTENANCE, CERT_TIRE_SPECIALIST)
  - `TASK_OIL_CHANGE` (required certs: CERT_BASIC_MAINTENANCE, CERT_ENGINE)

### VN-B787
- **Type:** Boeing 787 (`B787`)
- **Location:** HANGAR-02 (HANGAR)
  - Coordinates: (106.66, 10.819)
- **Time Window:** 2024-12-05T08:20:00Z → 2024-12-05T13:20:00Z
- **Required Tasks:** 2
  - `TASK_ENGINE_INSPECT` (required certs: CERT_ENGINE, CERT_INSPECTOR)
  - `TASK_CLEANING` (required certs: CERT_CLEANING)

## Hubs

### HUB_01
- **Location:** REST_AREA_A (HUB)
  - Coordinates: (106.665, 10.82)

## Employees

### MECHANIC

**EMP_001**
- Certificates: CERT_BASIC_MAINTENANCE, CERT_TIRE_SPECIALIST
- Current Location: `GATE-01`
- Working Times: 1 shift(s)
  - 2024-12-05T07:00:00Z → 2024-12-05T17:00:00Z
- Break Duration: 3600s (60 min)
- Fixed Break Times:
  - 2024-12-05T12:00:00Z → 2024-12-05T13:00:00Z

**EMP_002**
- Certificates: CERT_BASIC_MAINTENANCE, CERT_ENGINE, CERT_TIRE_SPECIALIST
- Current Location: `REST_AREA_A`
- Working Times: 1 shift(s)
  - 2024-12-05T07:00:00Z → 2024-12-05T17:00:00Z
- Break Duration: 3600s (60 min)
- Fixed Break Times:
  - 2024-12-05T12:00:00Z → 2024-12-05T13:00:00Z

### CLEANER

**EMP_003**
- Certificates: CERT_CLEANING
- Current Location: Not specified
- Working Times: 1 shift(s)
  - 2024-12-05T06:00:00Z → 2024-12-05T16:00:00Z
- Break Duration: 1800s (30 min)
- Fixed Break Times:
  - 2024-12-05T11:30:00Z → 2024-12-05T12:00:00Z

## Bus Stops

### BS_TERMINAL
- **Type:** Terminal Bus Stop (`TERMINAL_STOP`)
- **Coordinates:** (106.6588, 10.8185)

### BS_HANGAR
- **Type:** Hangar Area Bus Stop (`HANGAR_STOP`)
- **Coordinates:** (106.66, 10.819)

### BS_REST_AREA
- **Type:** Rest Area Bus Stop (`REST_AREA_STOP`)
- **Coordinates:** (106.665, 10.82)

## Bus Routes

### ROUTE_MAIN - Main Airport Loop
- **Cycle Time:** 1440s (24 min)
- **Frequency:** 1800s (30 min between departures)
- **Operating Hours:** 2024-12-05T06:00:00Z → 2024-12-05T18:00:00Z
- **Stops:** 4

| Stop | Arrival | Departure | Duration |
|------|---------|-----------|----------|
| BS_TERMINAL | 0 min | 2 min | 120s |
| BS_HANGAR | 8 min | 10 min | 120s |
| BS_REST_AREA | 16 min | 18 min | 120s |
| BS_TERMINAL | 24 min | Terminal | 0s |

## Matrices

### Distance Matrix
- Shape: (4, 4)
- Locations: 4
- Entries: 16

### Time Matrix
- Not available

### Bus Transit Matrix
- Shape: (3, 3)
- Bus Stops: 3
- Entries: 6

### Walking Distance to Bus Stops
- Shape: (4, 3)
- Entries: 3

