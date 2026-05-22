@echo off
REM DINO OS Setup Verification Script for Windows

echo.
echo ╔════════════════════════════════════════╗
echo ║    DINO OS - Setup Verification        ║
echo ╚════════════════════════════════════════╝
echo.

setlocal enabledelayedexpansion

REM Colors are limited in Windows CMD, so we'll use text instead
REM Check Node.js
echo Checking Node.js...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Node.js is installed
    node --version
) else (
    echo   [MISSING] Node.js not found
    echo   Install from: https://nodejs.org/
)

echo.

REM Check npm
echo Checking npm...
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] npm is installed
    npm --version
) else (
    echo   [MISSING] npm not found
)

echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Python is installed
    python --version
) else (
    echo   [MISSING] Python not found
    echo   Install from: https://python.org/
)

echo.

REM Check Git
echo Checking Git...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Git is installed
    git --version
) else (
    echo   [OPTIONAL] Git not found - optional for development
)

echo.
echo Checking project structure...
echo.

REM Check .env file
echo Checking .env file...
if exist .env (
    echo   [OK] .env file found
    findstr /M "GEMINI_API_KEY=" .env >nul 2>&1
    if !errorlevel! equ 0 (
        findstr "GEMINI_API_KEY=your_" .env >nul 2>&1
        if !errorlevel! equ 0 (
            echo   [WARN] API Key not configured
        ) else (
            echo   [OK] API Key appears to be configured
        )
    ) else (
        echo   [ERROR] API Key not found in .env
    )
) else (
    echo   [WARN] .env file not found
    echo   Create from .env.example: copy .env.example .env
)

echo.

REM Check frontend
echo Checking frontend...
if exist frontend\node_modules (
    echo   [OK] frontend/node_modules installed
) else (
    echo   [WARN] frontend/node_modules not installed
    echo   Run: cd frontend ^&^& npm install
)

echo.

REM Check backend venv
echo Checking backend...
if exist backend\venv (
    echo   [OK] backend/venv created
) else (
    echo   [WARN] backend/venv not created
    echo   Run: cd backend ^&^& python -m venv venv
)

echo.
echo ═══════════════════════════════════════
echo Setup verification complete!
echo.
echo Next steps:
echo   1. Configure .env with your Gemini API key
echo   2. Install dependencies:
echo      - cd frontend ^&^& npm install
echo      - cd backend ^&^& python -m venv venv
echo      - cd backend ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
echo   3. Start the application:
echo      - Run: start-dino.bat
echo.
echo Documentation:
echo   - QUICKSTART.md - 5-minute setup
echo   - README.md - Full documentation
echo   - DEVELOPER.md - Development guide
echo.
echo ═══════════════════════════════════════
echo.
pause
