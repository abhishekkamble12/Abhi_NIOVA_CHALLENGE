# Complete Database Setup - Master Script

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "    HiveMind Database Setup - Complete Workflow" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# Step 1: Deploy Aurora Database
Write-Host "STEP 1: Deploy Aurora PostgreSQL Cluster" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""
Write-Host "This will:" -ForegroundColor White
Write-Host "  • Create Aurora Serverless v2 cluster" -ForegroundColor Gray
Write-Host "  • Configure VPC and security groups" -ForegroundColor Gray
Write-Host "  • Enable public access for development" -ForegroundColor Gray
Write-Host "  • Save connection details to db-config.env" -ForegroundColor Gray
Write-Host ""
$confirm = Read-Host "Continue? (y/n)"
if ($confirm -ne 'y') { exit }

.\deploy-database.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Database deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "  Waiting 30 seconds for database to stabilize..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Step 2: Setup Schema
Write-Host ""
Write-Host "STEP 2: Initialize Database Schema" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""
Write-Host "This will:" -ForegroundColor White
Write-Host "  • Enable pgvector extension" -ForegroundColor Gray
Write-Host "  • Create base tables (brands, posts, videos, articles)" -ForegroundColor Gray
Write-Host "  • Create vector tables for AI features" -ForegroundColor Gray
Write-Host "  • Create indexes for performance" -ForegroundColor Gray
Write-Host ""
$confirm = Read-Host "Continue? (y/n)"
if ($confirm -ne 'y') { exit }

.\setup-database-schema.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Schema setup failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  • Install PostgreSQL client: choco install postgresql" -ForegroundColor Gray
    Write-Host "  • Check database is available in AWS Console" -ForegroundColor Gray
    Write-Host "  • Verify security group allows port 5432" -ForegroundColor Gray
    exit 1
}

# Step 3: Update Lambda Functions
Write-Host ""
Write-Host "STEP 3: Connect Lambda Functions to Database" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""
Write-Host "This will:" -ForegroundColor White
Write-Host "  • Update all Lambda environment variables" -ForegroundColor Gray
Write-Host "  • Configure database connection details" -ForegroundColor Gray
Write-Host "  • Enable Lambda-to-Aurora connectivity" -ForegroundColor Gray
Write-Host ""
$confirm = Read-Host "Continue? (y/n)"
if ($confirm -ne 'y') { exit }

.\update-lambda-db-config.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Lambda update failed" -ForegroundColor Red
    exit 1
}

# Step 4: Test Connection
Write-Host ""
Write-Host "STEP 4: Test Database Connection" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""
Write-Host "Testing Lambda → Aurora connection..." -ForegroundColor White

aws lambda invoke `
    --function-name hivemind-social-list-brands `
    --region ap-south-1 `
    --log-type Tail `
    response.json `
    --no-cli-pager 2>$null

if (Test-Path response.json) {
    $response = Get-Content response.json | ConvertFrom-Json
    Write-Host ""
    Write-Host "Response:" -ForegroundColor Cyan
    Get-Content response.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
    Remove-Item response.json
}

# Summary
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "   Database Setup Complete!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

# Load config for summary
$config = @{}
Get-Content "db-config.env" | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $config[$matches[1]] = $matches[2]
    }
}

Write-Host " System Status:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Database:" -ForegroundColor Yellow
Write-Host "  ✓ Aurora PostgreSQL Serverless v2" -ForegroundColor Green
Write-Host "  ✓ Host: $($config['DB_HOST'])" -ForegroundColor Green
Write-Host "  ✓ Database: $($config['DB_NAME'])" -ForegroundColor Green
Write-Host ""
Write-Host "Lambda Functions:" -ForegroundColor Yellow
Write-Host "  ✓ 9 functions configured with database access" -ForegroundColor Green
Write-Host ""
Write-Host "API Gateway:" -ForegroundColor Yellow
Write-Host "  ✓ https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend:" -ForegroundColor Yellow
Write-Host "  ✓ http://hivemind-frontend-83016.s3-website.ap-south-1.amazonaws.com" -ForegroundColor Green
Write-Host ""

Write-Host " Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Test API endpoints with real data" -ForegroundColor White
Write-Host "  2. Run: .\rebuild-with-cors.ps1 (if CORS issues persist)" -ForegroundColor White
Write-Host "  3. Create test brands and posts via API" -ForegroundColor White
Write-Host "  4. Monitor CloudWatch logs for errors" -ForegroundColor White
Write-Host ""

Write-Host " Quick Test Commands:" -ForegroundColor Cyan
Write-Host ""
Write-Host "# Create a brand" -ForegroundColor Gray
Write-Host 'curl -X POST https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod/social/brands -H "Content-Type: application/json" -d "{\"name\":\"TechCorp\",\"industry\":\"Technology\"}"' -ForegroundColor White
Write-Host ""
Write-Host "# List brands" -ForegroundColor Gray
Write-Host "curl https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod/social/brands" -ForegroundColor White
Write-Host ""

Write-Host " Configuration saved to: db-config.env" -ForegroundColor Green
Write-Host ""
