# HiveMind - Start Everything (Windows)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 HiveMind - Starting Full Stack" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$BACKEND_DIR = Join-Path $SCRIPT_DIR "backend-aws"
$FRONTEND_DIR = $SCRIPT_DIR

# Check backend
if (!(Test-Path $BACKEND_DIR)) {
    Write-Host "❌ Backend directory not found" -ForegroundColor Red
    exit 1
}

# Setup backend if needed
if (!(Test-Path "$BACKEND_DIR\venv")) {
    Write-Host "📦 Setting up backend..." -ForegroundColor Yellow
    cd $BACKEND_DIR
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
    Write-Host "✅ Backend setup complete" -ForegroundColor Green
}

# Check backend .env
if (!(Test-Path "$BACKEND_DIR\.env")) {
    Write-Host "❌ Backend .env not found" -ForegroundColor Red
    Write-Host "Run: copy backend-aws\.env.example backend-aws\.env"
    exit 1
}

# Check frontend .env.local
if (!(Test-Path "$FRONTEND_DIR\.env.local")) {
    Write-Host "📝 Creating frontend .env.local..." -ForegroundColor Yellow
    "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" | Out-File -FilePath "$FRONTEND_DIR\.env.local" -Encoding utf8
}

# Install frontend dependencies if needed
if (!(Test-Path "$FRONTEND_DIR\node_modules")) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
    cd $FRONTEND_DIR
    npm install
    Write-Host "✅ Frontend setup complete" -ForegroundColor Green
}

# Start backend
Write-Host ""
Write-Host "🔧 Starting Backend (port 8000)..." -ForegroundColor Yellow
cd $BACKEND_DIR
$backendJob = Start-Job -ScriptBlock {
    param($dir)
    cd $dir
    .\venv\Scripts\Activate.ps1
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
    uvicorn api_server:app --host 0.0.0.0 --port 8000
} -ArgumentList $BACKEND_DIR

Write-Host "✅ Backend started (Job ID: $($backendJob.Id))" -ForegroundColor Green

# Wait for backend
Write-Host "⏳ Waiting for backend..." -ForegroundColor Yellow
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 1 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Backend ready" -ForegroundColor Green
            break
        }
    } catch {}
    Start-Sleep -Seconds 1
}

# Start frontend
Write-Host ""
Write-Host "🎨 Starting Frontend (port 3000)..." -ForegroundColor Yellow
cd $FRONTEND_DIR
$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    cd $dir
    npm run dev
} -ArgumentList $FRONTEND_DIR

Write-Host "✅ Frontend started (Job ID: $($frontendJob.Id))" -ForegroundColor Green

# Save job IDs
"$($backendJob.Id)" | Out-File -FilePath "$SCRIPT_DIR\.backend.pid" -Encoding utf8
"$($frontendJob.Id)" | Out-File -FilePath "$SCRIPT_DIR\.frontend.pid" -Encoding utf8

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ HiveMind Running" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔗 Frontend:  http://localhost:3000"
Write-Host "🔗 Backend:   http://localhost:8000"
Write-Host "🔗 API Docs:  http://localhost:8000/docs"
Write-Host ""
Write-Host "📋 View Logs:"
Write-Host "   Get-Job | Receive-Job"
Write-Host ""
Write-Host "🛑 Stop: .\stop.ps1"
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan

# Keep running
Write-Host "Press Ctrl+C to stop..." -ForegroundColor Yellow
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "Stopping services..." -ForegroundColor Yellow
    Stop-Job $backendJob, $frontendJob
    Remove-Job $backendJob, $frontendJob
}
