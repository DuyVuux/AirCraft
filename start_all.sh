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

echo "Waiting for log files to initialize..."
sleep 2

echo "Opening separate windows for logs..."
# Open 3 bash windows to tail logs depending on terminal emulator availability
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal --title="Backend API Log" -- bash -c "tail -f AirCraft/backend/backend.log; exec bash" &
    gnome-terminal --title="Algorithm Engine Log" -- bash -c "tail -f AirCraft_algo/algo.log; exec bash" &
    gnome-terminal --title="Frontend React Log" -- bash -c "tail -f AirCraft/frontend/frontend.log; exec bash" &
elif command -v x-terminal-emulator &> /dev/null; then
    x-terminal-emulator -T "Backend API Log" -e bash -c "tail -f AirCraft/backend/backend.log; exec bash" &
    x-terminal-emulator -T "Algorithm Engine Log" -e bash -c "tail -f AirCraft_algo/algo.log; exec bash" &
    x-terminal-emulator -T "Frontend React Log" -e bash -c "tail -f AirCraft/frontend/frontend.log; exec bash" &
else
    echo "Could not find a terminal emulator (gnome-terminal/x-terminal-emulator) to open log windows."
    echo "You can check logs manually using tail -f <logfile>."
fi

echo "All services started in background!"
echo "- Frontend React: http://localhost:5173"
echo "- Backend API: http://localhost:8002"
echo "- Algo Engine: http://localhost:8001"
