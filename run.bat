@echo off
title RecoverAI — 1-Click Launcher
echo =====================================================================
echo           RecoverAI — AI Payment Recovery Platform Launcher
echo =====================================================================
echo.

:: 1. Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python 3.10+.
    pause
    exit /b 1
)

:: 2. Check Node
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js/NPM is not installed! Please install Node.js 18+.
    pause
    exit /b 1
)

:: 3. Setup Python Virtual Environment
if not exist "venv" (
    echo [*] Creating Python Virtual Environment (venv)...
    python -m venv venv
    call .\venv\Scripts\activate
    echo [*] Installing Python backend dependencies...
    pip install -r requirements.txt
) else (
    call .\venv\Scripts\activate
)

:: 4. Setup Frontend Dependencies
if not exist "frontend\node_modules" (
    echo [*] Installing Frontend NPM dependencies...
    cd frontend
    call npm install
    cd ..
)

:: 5. Copy sample .env if not exists
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [*] Initialized default .env from .env.example
    )
)

echo.
echo =====================================================================
echo   [OK] Launching RecoverAI Backend (Port 8000) and Frontend (Port 3000)
echo =====================================================================
echo.

:: Start Backend in background window
start "RecoverAI Backend" cmd /k ".\venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

:: Start Frontend in background window
start "RecoverAI Frontend" cmd /k "cd frontend && npm run dev -- --port 3000"

:: Wait 3 seconds and open browser
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo [SUCCESS] RecoverAI is running at http://localhost:3000
echo Backend API Docs at http://localhost:8000/docs
echo.
pause
