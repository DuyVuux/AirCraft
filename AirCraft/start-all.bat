@echo off
REM Script to start both frontend and backend servers simultaneously on Windows

echo ========================================
echo  Starting Aircraft Web Application
echo ========================================

REM Activate virtual environment
echo [1/4] Activating virtual environment...
if not exist "%~dp0venv" (
    echo Virtual environment not found. Creating it...
    python -m venv "%~dp0venv"
)
call "%~dp0venv\Scripts\activate"

REM Install dependencies
echo [2/4] Installing backend dependencies...
pip install -r "%~dp0requirements.txt" > nul 2>&1

REM Start backend in a new command window
echo [3/4] Starting Backend Server...
start "Backend Server" cmd /k "cd /d %~dp0backend && call ..\venv\Scripts\activate && python main.py"

REM Wait a moment for backend to start
timeout /t 5 /nobreak > nul

REM Start frontend in a new command window  
echo [4/4] Starting Frontend Server...
start "Frontend Server" cmd /k "cd /d %~dp0frontend && npm install && npm run dev"

echo ========================================
echo  Both servers are starting!
echo  - Backend:  http://localhost:8000
echo  - Frontend: http://localhost:5173
echo ========================================
echo.
echo Press any key to close this window (servers will keep running)
pause > nul
