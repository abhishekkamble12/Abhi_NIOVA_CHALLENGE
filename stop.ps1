# HiveMind - Stop Everything (Windows)

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🛑 Stopping HiveMind" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Stop backend job
if (Test-Path "$SCRIPT_DIR\.backend.pid") {
    $backendJobId = Get-Content "$SCRIPT_DIR\.backend.pid"
    $job = Get-Job -Id $backendJobId -ErrorAction SilentlyContinue
    if ($job) {
        Write-Host "🔧 Stopping backend (Job ID: $backendJobId)..." -ForegroundColor Yellow
        Stop-Job -Id $backendJobId
        Remove-Job -Id $backendJobId
        Write-Host "✅ Backend stopped" -ForegroundColor Green
    }
    Remove-Item "$SCRIPT_DIR\.backend.pid"
}

# Stop frontend job
if (Test-Path "$SCRIPT_DIR\.frontend.pid") {
    $frontendJobId = Get-Content "$SCRIPT_DIR\.frontend.pid"
    $job = Get-Job -Id $frontendJobId -ErrorAction SilentlyContinue
    if ($job) {
        Write-Host "🎨 Stopping frontend (Job ID: $frontendJobId)..." -ForegroundColor Yellow
        Stop-Job -Id $frontendJobId
        Remove-Job -Id $frontendJobId
        Write-Host "✅ Frontend stopped" -ForegroundColor Green
    }
    Remove-Item "$SCRIPT_DIR\.frontend.pid"
}

# Kill processes on ports
Write-Host "🧹 Cleaning up ports..." -ForegroundColor Yellow
Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*next*"} | Stop-Process -Force

Write-Host ""
Write-Host "✅ HiveMind stopped" -ForegroundColor Green
