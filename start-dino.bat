@echo off
REM DINO OS Startup Script for Windows

echo.
echo ╔════════════════════════════════════════╗
echo ║        DINO OS - Startup Script        ║
echo ║   Futuristic AI Desktop Assistant      ║
echo ╚════════════════════════════════════════╝
echo.

REM Check if .env file exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo Please copy .env.example to .env and configure your API key.
    pause
    exit /b 1
)

REM Check if backend venv exists
if not exist "backend\venv" (
    echo [INFO] Creating Python virtual environment...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [INFO] Installing backend dependencies...
    pip install -r requirements.txt
    cd ..
)

REM Check if frontend node_modules exists
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

echo.
echo [INFO] Starting DINO OS...
echo.
echo Starting backend server (Terminal 1)...
echo Starting frontend application (Terminal 2)...
echo.
echo Note: Press Ctrl+C to stop either service
echo.

REM Start backend in new terminal
start cmd /k "cd backend & call venv\Scripts\activate.bat & python -m uvicorn main:app --reload --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Start frontend in new terminal
start cmd /k "cd frontend & npm start"

echo.
echo [SUCCESS] DINO OS is starting!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo.
pause
