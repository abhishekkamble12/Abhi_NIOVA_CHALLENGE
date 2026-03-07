# HiveMind Complete Deployment Script
# Deploys entire serverless backend infrastructure

$ErrorActionPreference = "Stop"

Write-Host "🚀 HiveMind Serverless Backend Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$S3_BUCKET = "media-ai-content"
$REGION = "ap-south-1"
$ACCOUNT_ID = "586098609294"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  S3 Bucket: $S3_BUCKET" -ForegroundColor White
Write-Host "  Region: $REGION" -ForegroundColor White
Write-Host "  Account: $ACCOUNT_ID" -ForegroundColor White
Write-Host ""

# Deployment order
$steps = @(
    @{Number=1; Name="Deploy Lambda Layer"; Script="1-deploy-layer.ps1"},
    @{Number=2; Name="Create IAM Role"; Script="2-create-iam-role.ps1"},
    @{Number=3; Name="Deploy Lambda Functions"; Script="3-deploy-lambdas.ps1"},
    @{Number=4; Name="Create API Gateway"; Script="4-create-api-gateway.ps1"},
    @{Number=5; Name="Create Step Functions"; Script="5-create-step-functions.ps1"}
)

foreach ($step in $steps) {
    Write-Host "[$($step.Number)/5] $($step.Name)..." -ForegroundColor Cyan
    
    & ".\$($step.Script)"
    
    if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne $null) {
        Write-Host "❌ Step $($step.Number) failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
}

# Summary
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "layer-arn.txt") {
    $layerArn = Get-Content "layer-arn.txt"
    Write-Host "Lambda Layer: $layerArn" -ForegroundColor White
}

if (Test-Path "api-url.txt") {
    $apiUrl = Get-Content "api-url.txt"
    Write-Host "API Gateway: $apiUrl" -ForegroundColor White
}

if (Test-Path "state-machine-arn.txt") {
    $sfnArn = Get-Content "state-machine-arn.txt"
    Write-Host "Step Functions: $sfnArn" -ForegroundColor White
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update Lambda environment variables with actual database credentials" -ForegroundColor Gray
Write-Host "2. Test API endpoints: curl $apiUrl/social/brands" -ForegroundColor Gray
Write-Host "3. Test Step Functions with sample video upload" -ForegroundColor Gray
Write-Host "4. Configure CloudWatch alarms for monitoring" -ForegroundColor Gray
