#!/bin/bash
pkill -f uvicorn
pkill -f "python3 main.py"
pkill -f vite

echo "Starting FastAPI Backend..."
cd AirCraft/backend/
source .venv/bin/activate
nohup uvicorn main:app --env-file .env --reload --port 8002 > backend.log 2>&1 &
cd ../..

echo "Starting Flask Algorithm Engine..."
cd AirCraft_algo/
source .venv/bin/activate
nohup python3 main.py > algo.log 2>&1 &
cd ..

echo "Starting React Frontend..."
cd AirCraft/frontend/
nohup npm run dev > frontend.log 2>&1 &
cd ../..

echo "All services started in background!"
echo "- Frontend React: http://localhost:5173"
echo "- Backend API: http://localhost:8002"
echo "- Algo Engine: http://localhost:8001"
