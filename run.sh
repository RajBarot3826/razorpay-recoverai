#!/bin/bash
set -e

echo "====================================================================="
echo "          RecoverAI — AI Payment Recovery Platform Launcher"
echo "====================================================================="
echo ""

if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[ERROR] Python 3 is required. Please install Python 3.10+."
        exit 1
    else
        PY_CMD=python
    fi
else
    PY_CMD=python3
fi

if ! command -v npm &> /dev/null; then
    echo "[ERROR] Node.js/NPM is required. Please install Node.js 18+."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "[*] Creating Python Virtual Environment (venv)..."
    $PY_CMD -m venv venv
    source venv/bin/activate
    echo "[*] Installing backend dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "[*] Installing frontend dependencies..."
    cd frontend && npm install && cd ..
fi

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "[*] Created default .env from .env.example"
    fi
fi

echo ""
echo "====================================================================="
echo "  [OK] Launching RecoverAI Backend (:8000) and Frontend (:3000)"
echo "====================================================================="
echo ""

uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cd frontend && npm run dev -- --port 3000 &
FRONTEND_PID=$!

echo "[SUCCESS] RecoverAI is running!"
echo "[*] Frontend: http://localhost:3000"
echo "[*] Backend:  http://localhost:8000/docs"

if which xdg-open > /dev/null; then
    xdg-open http://localhost:3000 &> /dev/null || true
elif which open > /dev/null; then
    open http://localhost:3000 &> /dev/null || true
fi

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
