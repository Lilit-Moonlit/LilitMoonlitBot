@echo off
title Beauty Bot - Lilit
cd /d "%~dp0"

echo [1/3] Checking environment...
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment 'venv' not found in %cd%
    pause
    exit /b
)

echo [2/3] Stopping any running bot instances...
powershell -Command "Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force" 2>nul
timeout /t 1 /nobreak >nul

echo [3/3] Starting Lilit Bot...
set PYTHONIOENCODING=utf-8
venv\Scripts\python.exe -m app.main

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Bot stopped with exit code %ERRORLEVEL%
)

echo.
echo Press any key to exit...
pause
