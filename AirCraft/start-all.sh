#!/bin/bash

# Script to start both frontend and backend servers simultaneously

echo "========================================"
echo " Starting Aircraft Web Application"
echo "========================================"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Setup virtual environment at root
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt" --quiet

# Start backend
echo "[1/2] Starting Backend Server..."
cd "$SCRIPT_DIR/backend"
echo "🚀 Backend starting on http://localhost:8000"
python main.py &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# Wait for backend to start
sleep 3

# Start frontend
echo "[2/2] Starting Frontend Server..."
cd "$SCRIPT_DIR/frontend"
npm install --silent
echo "🚀 Frontend starting on http://localhost:5173"
npm run dev &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

echo ""
echo "========================================"
echo " Both servers are running!"
echo " - Backend:  http://localhost:8000"
echo " - Frontend: http://localhost:5173"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for both processes
wait
