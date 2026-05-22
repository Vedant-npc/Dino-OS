@echo off
REM DINO OS - System-Wide Launch Script
REM This script starts both the backend and frontend services

setlocal enabledelayedexpansion

echo.
echo ════════════════════════════════════════════════════════════
echo   🚀 DINO OS - Futuristic AI Desktop Assistant
echo ════════════════════════════════════════════════════════════
echo.

cd /d d:\My_Projects\DINO

REM Check if .env file exists
if not exist .env (
    echo ❌ ERROR: .env file not found!
    echo.
    echo Please create .env file with:
    echo   GEMINI_API_KEY=your_key_here
    echo.
    echo Get your free API key from: https://makersuite.google.com/app/apikey
    echo.
    pause
    exit /b 1
)

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: Node.js not found!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: Python not found!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo ✓ Node.js found
echo ✓ Python found
echo ✓ Configuration file found
echo.

REM Start backend
echo ════════════════════════════════════════════════════════════
echo   Starting Backend (FastAPI on port 8000)...
echo ════════════════════════════════════════════════════════════
echo.

cd /d d:\My_Projects\DINO\backend
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
python -m uvicorn main:app --reload --port 8000 >%TEMP%\dino-backend.log 2>&1 &
set BACKEND_PID=!ERRORLEVEL!

echo ✓ Backend started (PID: %BACKEND_PID%)
echo ✓ Backend logs: %TEMP%\dino-backend.log
echo.

REM Wait for backend to be ready
echo Waiting for backend to be ready...
timeout /t 3 /nobreak

REM Test backend
powershell -Command "try { [void](Invoke-WebRequest -Uri 'http://localhost:8000/health' -ErrorAction Stop); Write-Host '✓ Backend is ready'; exit 0 } catch { Write-Host '⚠ Backend may still be starting...'; exit 1 }"

echo.
echo ════════════════════════════════════════════════════════════
echo   Starting Frontend (React on port 3001)...
echo ════════════════════════════════════════════════════════════
echo.

cd /d d:\My_Projects\DINO\frontend

if not exist node_modules (
    echo Installing npm dependencies...
    call npm install --legacy-peer-deps
)

echo ✓ Starting React development server...
call npm start

REM Note: npm start will run in foreground, blocking until stopped
