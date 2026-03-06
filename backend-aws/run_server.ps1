# Start HiveMind Backend Server (Windows)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Starting HiveMind Backend Server" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Activate virtual environment
if (Test-Path venv) {
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "❌ Virtual environment not found. Run .\start.ps1 first" -ForegroundColor Red
    exit 1
}

# Check .env
if (!(Test-Path .env)) {
    Write-Host "❌ .env file not found" -ForegroundColor Red
    exit 1
}

# Load environment
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

Write-Host "✅ Environment loaded" -ForegroundColor Green
Write-Host "✅ Starting FastAPI server on port 8000..." -ForegroundColor Green
Write-Host ""

# Start server
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
