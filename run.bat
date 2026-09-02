@echo off
setlocal enabledelayedexpansion
title RecoverAI — 1-Click Zero-Friction Launcher

echo =====================================================================
echo           RecoverAI — AI Payment Recovery Platform Launcher
echo =====================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not installed or not in PATH! Please install Python 3.10+.
        pause
        exit /b 1
    )
    set PY_CMD=py -3
) else (
    set PY_CMD=python
)

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js/NPM is not installed! Please install Node.js 18+.
    pause
    exit /b 1
)

if not exist "venv" (
    echo [*] Initializing Python Virtual Environment (venv)...
    !PY_CMD! -m venv venv
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
    )
    echo [*] Installing backend dependencies...
    pip install -r requirements.txt
) else (
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
    )
)

if not exist "frontend\node_modules" (
    echo [*] Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [*] Initialized default configuration from .env.example
    )
)

echo.
echo =====================================================================
echo   [OK] Launching RecoverAI Backend (:8000) and Frontend (:3000)
echo =====================================================================
echo.

start "RecoverAI Backend" cmd /k "venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

start "RecoverAI Frontend" cmd /k "cd frontend && npm run dev -- --port 3000"

timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo [SUCCESS] RecoverAI is running!
echo [*] Frontend Web App: http://localhost:3000
echo [*] Backend API Docs: http://localhost:8000/docs
echo.
pause
