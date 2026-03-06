# HiveMind AWS Backend Startup (No AWS CLI/SDK Required)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 HiveMind AWS Backend Startup" -ForegroundColor Cyan
Write-Host "   (Python 3.11 Required | No AWS CLI/SDK)" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan

# --------------------------------------------

# Check .env file

# --------------------------------------------

if (!(Test-Path .env)) {
Write-Host "❌ .env file not found" -ForegroundColor Red
Copy-Item .env.example .env
Write-Host "⚠️ Configure .env and run again" -ForegroundColor Yellow
exit 1
}

# --------------------------------------------

# Load environment variables

# --------------------------------------------

Get-Content .env | ForEach-Object {
if ($_ -match '^([^#][^=]+)=(.*)$') {
[Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
}
}

Write-Host "✅ Environment variables loaded" -ForegroundColor Green

# --------------------------------------------

# Check Python 3.11

# --------------------------------------------

Write-Host "Checking Python 3.11..."

$pythonVersion = py -3.11 --version 2>&1

if ($LASTEXITCODE -ne 0) {
Write-Host "❌ Python 3.11 not installed"
exit 1
}

Write-Host "✅ $pythonVersion detected"

# --------------------------------------------

# Create virtual environment

# --------------------------------------------

if (!(Test-Path venv)) {
Write-Host "Creating Python 3.11 virtual environment..."
py -3.11 -m venv venv
}

# --------------------------------------------

# Activate virtual environment

# --------------------------------------------

.\venv\Scripts\Activate.ps1
$pythonExe = ".\venv\Scripts\python.exe"

# --------------------------------------------

# Install dependencies

# --------------------------------------------

Write-Host "Installing dependencies..."

& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
Write-Host "❌ Dependency installation failed"
exit 1
}

Write-Host "✅ Dependencies installed"

# --------------------------------------------

# Test Aurora

# --------------------------------------------

Write-Host "Testing Aurora PostgreSQL..."

$temp = "temp_test.py"

@"
import asyncio
from services.aurora_service import get_db_connection

async def test():
try:
async with get_db_connection() as conn:
await conn.fetchval('SELECT 1')
print("Aurora connected")
except Exception as e:
print("Aurora error:", e)

asyncio.run(test())
"@ | Out-File $temp -Encoding utf8

& $pythonExe $temp
Remove-Item $temp

# --------------------------------------------

# Test Redis

# --------------------------------------------

Write-Host "Testing Redis..."

@"
import asyncio
from services.cache_service import get_cache_service

async def test():
try:
cache = get_cache_service()
await cache.set("test","ok",ttl=10)
print("Redis connected")
except Exception as e:
print("Redis error:", e)

asyncio.run(test())
"@ | Out-File $temp -Encoding utf8

& $pythonExe $temp
Remove-Item $temp

# --------------------------------------------

# Test S3

# --------------------------------------------

Write-Host "Testing S3..."

@"
import asyncio
from services.s3_service import get_s3_service

async def test():
try:
s3 = get_s3_service()
await s3.head_file("test.txt")
print("S3 access OK")
except Exception as e:
print("S3 error:", e)

asyncio.run(test())
"@ | Out-File $temp -Encoding utf8

& $pythonExe $temp
Remove-Item $temp

# --------------------------------------------

# Test Bedrock

# --------------------------------------------

Write-Host "Testing Bedrock..."

@"
import asyncio
from services.bedrock_service import get_bedrock_service

async def test():
try:
bedrock = get_bedrock_service()
await bedrock.generate_embedding("test")
print("Bedrock API OK")
except Exception as e:
print("Bedrock error:", e)

asyncio.run(test())
"@ | Out-File $temp -Encoding utf8

& $pythonExe $temp
Remove-Item $temp

Write-Host ""
Write-Host "=========================================="
Write-Host "HiveMind backend ready"
Write-Host "=========================================="
Write-Host ""
Write-Host "Run application:"
Write-Host "python start.py"
