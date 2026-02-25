# 🧠 AirCraft Optimization Engine

This module serves as the dedicated mathematical modeling and computational brain for the AirCraft System. Deployed as an independent **Flask Server**, it decouples intense algorithmic processing from the core data API.

## 📋 Capabilities

The engine solves the complex Aircraft Maintenance Scheduling routing problem, balancing the following strict constraints:
- Employee Certifications vs Task Requirements.
- Precedence (e.g., Task B cannot start until Task A finishes).
- Pairwise Travel Distances via location-aware mapping.
- Non-Overlapping Working Windows & Mandatory Break Intervals.

## 🚀 Running the Engine Local

Ensure you have Python 3.9+ installed on your system.

```bash
# 1. Navigate to the directory
cd AirCraft_algo

# 2. Create and activate a Virtual Environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Boot the server
python3 main.py
```

The Flask server will start on port `8001`.

**Important Internal URLs:**
- `http://localhost:8001/` - Solutions Dashboard.
- `http://localhost:8001/benchmark` - Built-in Algorithm Comparison Tool.

## 💡 Algorithmic Strategies

The engine exposes multiple solvers dependent on the size of the instance:

1. **Greedy Strategy (Fast Heuristic)**
   - Uses Topological Sort to execute tasks immediately when dependencies are clear.
   - Respects scheduled break times (`NoOverlap2D` proxies).
2. **Pure CP-SAT (`OrStrategy`)**
   - Direct execution via Google OR-Tools. Perfect for finding the mathematically `OPTIMAL` solution in small instances.
3. **Hybrid LNS (Large Neighborhood Search)**
   - Recommended for Production. Employs a 'Destroy and Repair' loop over a greedy initialization.
   - Evaluates transitions via **Simulated Annealing** (Boltzmann acceptance) mapped strongly against a custom cost scalar ($100M for dropped tasks).

## 📊 Run Benchmarks 

You can use the built-in UI at `http://localhost:8001/benchmark` or hit the API directly:

```bash
curl -X POST http://localhost:8001/api/benchmark/run \
  -H "Content-Type: application/json" \
  -d '{
    "strategies": ["cpsat", "lns"],
    "sizes": ["small", "medium"],
    "time_limit": 30
  }'
```

## 🧪 Testing

The engine is heavily tested using `pytest`.

```bash
# Run all unit and integration tests
pytest tests/
```
