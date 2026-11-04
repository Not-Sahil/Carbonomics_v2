# Carbonomics v3 — Start Device Telemetry Agent (Windows PowerShell)
param (
    [string]$Server = "http://localhost:5000",
    [string]$Region = "ap-south-1",
    [string]$DeviceType = "laptop"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $ScriptDir "..")

Write-Host "🔌 Carbonomics v3 Device Agent starting..." -ForegroundColor Green
Write-Host "   Server: $Server | Region: $Region | Type: $DeviceType" -ForegroundColor Gray

if (Test-Path ".venv\Scripts\Activate.ps1") {
    & .venv\Scripts\Activate.ps1
    & .venv\Scripts\python.exe device_agent/agent.py --server $Server --region $Region --device-type $DeviceType
} else {
    python device_agent/agent.py --server $Server --region $Region --device-type $DeviceType
}

