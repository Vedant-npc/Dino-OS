#!/bin/bash

# DINO OS Startup Script for macOS/Linux

echo ""
echo "╔════════════════════════════════════════╗"
echo "║        DINO OS - Startup Script        ║"
echo "║   Futuristic AI Desktop Assistant      ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "[ERROR] .env file not found!"
    echo "Please copy .env.example to .env and configure your API key."
    exit 1
fi

# Check if backend venv exists
if [ ! -d "backend/venv" ]; then
    echo "[INFO] Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    echo "[INFO] Installing backend dependencies..."
    pip install -r requirements.txt
    cd ..
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "[INFO] Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "[INFO] Starting DINO OS..."
echo ""
echo "Starting backend server..."
echo "Starting frontend application..."
echo ""
echo "Note: Press Ctrl+C to stop any service"
echo ""

# Start backend in background
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "[SUCCESS] DINO OS is starting!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""

# Wait for both processes
wait
