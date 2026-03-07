# Cleanup Script - Remove All Deployed Resources

$ErrorActionPreference = "Continue"

Write-Host "🗑️  HiveMind Infrastructure Cleanup" -ForegroundColor Red
Write-Host "====================================" -ForegroundColor Red
Write-Host ""
Write-Host "⚠️  WARNING: This will delete all deployed resources!" -ForegroundColor Yellow
Write-Host ""

$confirmation = Read-Host "Type 'DELETE' to confirm"
if ($confirmation -ne "DELETE") {
    Write-Host "Cleanup cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""

# Step 1: Delete Step Functions
if (Test-Path "state-machine-arn.txt") {
    Write-Host "[1/5] Deleting Step Functions..." -ForegroundColor Cyan
    $sfnArn = Get-Content "state-machine-arn.txt"
    aws stepfunctions delete-state-machine --state-machine-arn $sfnArn
    Write-Host "  ✅ State machine deleted" -ForegroundColor Green
}

# Step 2: Delete API Gateway
if (Test-Path "api-id.txt") {
    Write-Host "[2/5] Deleting API Gateway..." -ForegroundColor Cyan
    $apiId = Get-Content "api-id.txt"
    aws apigateway delete-rest-api --rest-api-id $apiId
    Write-Host "  ✅ API Gateway deleted" -ForegroundColor Green
}

# Step 3: Delete Lambda Functions
Write-Host "[3/5] Deleting Lambda Functions..." -ForegroundColor Cyan
$functions = aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `hivemind-`)].FunctionName' --output text
foreach ($func in $functions -split '\s+') {
    aws lambda delete-function --function-name $func 2>$null
    Write-Host "  ✅ Deleted $func" -ForegroundColor Green
}

# Step 4: Delete Lambda Layer
Write-Host "[4/5] Deleting Lambda Layer..." -ForegroundColor Cyan
$versions = aws lambda list-layer-versions --layer-name hivemind-shared-layer --query 'LayerVersions[*].Version' --output text
foreach ($version in $versions -split '\s+') {
    aws lambda delete-layer-version --layer-name hivemind-shared-layer --version-number $version 2>$null
}
Write-Host "  ✅ Lambda layer deleted" -ForegroundColor Green

# Step 5: Delete IAM Roles
Write-Host "[5/5] Deleting IAM Roles..." -ForegroundColor Cyan

# Lambda execution role
aws iam delete-role-policy --role-name hivemind-lambda-execution-role --policy-name hivemind-lambda-policy 2>$null
aws iam detach-role-policy --role-name hivemind-lambda-execution-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>$null
aws iam delete-role --role-name hivemind-lambda-execution-role 2>$null

# Step Functions role
aws iam delete-role-policy --role-name hivemind-stepfunctions-role --policy-name StepFunctionsLambdaInvoke 2>$null
aws iam delete-role --role-name hivemind-stepfunctions-role 2>$null

Write-Host "  ✅ IAM roles deleted" -ForegroundColor Green

# Clean up output files
Remove-Item -Path "*.txt" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✅ Cleanup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Note: S3 bucket 'media-ai-content' was NOT deleted (contains your code)" -ForegroundColor Yellow
