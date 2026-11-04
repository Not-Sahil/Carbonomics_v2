# Carbonomics v3 — Start Backend (Windows PowerShell)
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $ScriptDir "..")

Write-Host "🌿 Carbonomics v3 — Starting Enterprise Backend..." -ForegroundColor Green

if (Test-Path ".venv\Scripts\Activate.ps1") {
    & .venv\Scripts\Activate.ps1
    & .venv\Scripts\python.exe backend/api/app.py
} else {
    python backend/api/app.py
}

