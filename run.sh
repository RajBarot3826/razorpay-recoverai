#!/bin/bash
# RecoverAI — 1-Click Launcher (Linux / macOS)

set -e

echo "====================================================================="
echo "          RecoverAI — AI Payment Recovery Platform Launcher"
echo "====================================================================="
echo ""

# 1. Setup Python Virtual Environment
if [ ! -d "venv" ]; then
    echo "[*] Creating Python Virtual Environment (venv)..."
    python3 -m venv venv
    source venv/bin/activate
    echo "[*] Installing Python backend dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 2. Setup Frontend Dependencies
if [ ! -d "frontend/node_modules" ]; then
    echo "[*] Installing Frontend dependencies..."
    cd frontend && npm install && cd ..
fi

# 3. Setup .env
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "[*] Created .env from .env.example"
    fi
fi

echo ""
echo "====================================================================="
echo "  [OK] Launching RecoverAI Backend (Port 8000) and Frontend (Port 3000)"
echo "====================================================================="
echo ""

# Start backend in background
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start frontend in background
cd frontend && npm run dev -- --port 3000 &
FRONTEND_PID=$!

echo "[SUCCESS] RecoverAI is running!"
echo "👉 Frontend: http://localhost:3000"
echo "👉 Backend:  http://localhost:8000/docs"

# Wait for both processes
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
