Write-Host "[1/2] Checking environment..." -ForegroundColor Cyan
$pythonPath = Join-Path $PSScriptRoot ".venv312\Scripts\python.exe"

if (!(Test-Path $pythonPath)) {
    Write-Host "ERROR: Virtual environment '.venv312' not found in $PSScriptRoot" -ForegroundColor Red
    Read-Host "Press Enter to exit..."
    exit
}

Write-Host "[2/2] Starting Freya Bot..." -ForegroundColor Green
$env:PYTHONIOENCODING = "utf-8"
& $pythonPath -m app.main

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nERROR: Bot stopped with exit code $LASTEXITCODE" -ForegroundColor Red
}

Read-Host "`nPress Enter to exit..."
