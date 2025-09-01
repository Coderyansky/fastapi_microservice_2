# Complete Service Launcher for FastAPI User Management System (PowerShell)
# This PowerShell script starts both the FastAPI backend and GUI application

param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 8000,
    [int]$GuiDelay = 3,
    [switch]$NoGui,
    [switch]$Help
)

function Show-Help {
    Write-Host @"
FastAPI User Management Service Launcher (PowerShell)

USAGE:
    .\start_service.ps1 [options]

OPTIONS:
    -Host <string>      Backend host address (default: 127.0.0.1)
    -Port <int>         Backend port number (default: 8000)
    -GuiDelay <int>     Delay in seconds before starting GUI (default: 3)
    -NoGui              Start only the backend service without GUI
    -Help               Show this help message

EXAMPLES:
    .\start_service.ps1                           # Start both backend and GUI
    .\start_service.ps1 -Port 8080               # Use custom port
    .\start_service.ps1 -NoGui                   # Backend only
    .\start_service.ps1 -Host 0.0.0.0 -Port 8000 # Custom host and port
"@
}

if ($Help) {
    Show-Help
    exit 0
}

Write-Host "FastAPI User Management Service Launcher" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Yellow
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Error: Virtual environment not found" -ForegroundColor Red
    Write-Host "Please create virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor Cyan
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Cyan
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to activate virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Build arguments for launcher.py
$launcherArgs = @("launcher.py")
$launcherArgs += "--host", $Host
$launcherArgs += "--port", $Port.ToString()
$launcherArgs += "--gui-delay", $GuiDelay.ToString()

if ($NoGui) {
    $launcherArgs += "--no-gui"
}

Write-Host "Starting complete service stack..." -ForegroundColor Green
Write-Host "Command: python $($launcherArgs -join ' ')" -ForegroundColor Cyan

try {
    & python @launcherArgs
} catch {
    Write-Host "Error: Failed to start service" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host "Service stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"