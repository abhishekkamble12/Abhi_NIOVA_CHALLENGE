# Setup Database Schema

param(
    [string]$ConfigFile = "db-config.env"
)

Write-Host " Setting Up Database Schema" -ForegroundColor Cyan
Write-Host ""

# Load config
if (Test-Path $ConfigFile) {
    Get-Content $ConfigFile | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            Set-Variable -Name $matches[1] -Value $matches[2]
        }
    }
    Write-Host " Loaded config from $ConfigFile" -ForegroundColor Green
} else {
    Write-Host " Config file not found: $ConfigFile" -ForegroundColor Red
    Write-Host "Run deploy-database.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Check if psql is available
$psqlExists = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psqlExists) {
    Write-Host " psql not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install PostgreSQL client:" -ForegroundColor Yellow
    Write-Host "  choco install postgresql" -ForegroundColor Gray
    Write-Host "  or download from: https://www.postgresql.org/download/windows/" -ForegroundColor Gray
    exit 1
}

$env:PGPASSWORD = $DB_PASSWORD

Write-Host ""
Write-Host "Connecting to database..." -ForegroundColor Yellow
Write-Host "  Host: $DB_HOST" -ForegroundColor Gray

# Test connection
$testResult = psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT version();" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host " Connection failed" -ForegroundColor Red
    Write-Host $testResult
    exit 1
}

Write-Host " Connected" -ForegroundColor Green

# Enable pgvector extension
Write-Host ""
Write-Host "Enabling pgvector extension..." -ForegroundColor Yellow
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host " pgvector enabled" -ForegroundColor Green
} else {
    Write-Host " pgvector not available (optional)" -ForegroundColor Yellow
}

# Run base schema
Write-Host ""
Write-Host "Creating base tables..." -ForegroundColor Yellow
$schemaPath = "..\backend-aws\schema.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f $schemaPath
if ($LASTEXITCODE -eq 0) {
    Write-Host " Base schema created" -ForegroundColor Green
} else {
    Write-Host " Schema creation failed" -ForegroundColor Red
    exit 1
}

# Run vector schema
Write-Host ""
Write-Host "Setting up vector tables..." -ForegroundColor Yellow
$vectorSchemaPath = "..\db-setup\schema_vector.sql"
if (Test-Path $vectorSchemaPath) {
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f $vectorSchemaPath 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host " Vector schema created" -ForegroundColor Green
    } else {
        Write-Host " Vector schema skipped" -ForegroundColor Yellow
    }
}

# Verify tables
Write-Host ""
Write-Host "Verifying tables..." -ForegroundColor Yellow
$tables = psql -h $DB_HOST -U $DB_USER -d $DB_NAME -t -c "\dt" | Select-String -Pattern "public"
$tableCount = ($tables | Measure-Object).Count
Write-Host " $tableCount tables created" -ForegroundColor Green

Write-Host ""
Write-Host " Database Schema Ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Tables:" -ForegroundColor Cyan
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\dt"

$env:PGPASSWORD = $null
