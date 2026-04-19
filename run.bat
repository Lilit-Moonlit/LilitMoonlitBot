@echo off
title Beauty Bot - Fast Run

if exist venv\Scripts\python.exe (
    echo [OK] Starting bot using venv...
    venv\Scripts\python.exe -m app.main
    goto :EOF
)

if exist .venv312\Scripts\python.exe (
    echo [OK] Starting bot using .venv312...
    .venv312\Scripts\python.exe -m app.main
    goto :EOF
)

echo [ERROR] Virtual environment not found (checked venv and .venv312)
pause
