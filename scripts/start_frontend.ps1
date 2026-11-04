# Carbonomics v3 — Start Frontend Dashboard (Windows PowerShell)
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $ScriptDir "..\frontend")

Write-Host "⚡ Carbonomics v3 — Starting Enterprise Frontend Dashboard on http://localhost:3000..." -ForegroundColor Cyan
npm run dev
