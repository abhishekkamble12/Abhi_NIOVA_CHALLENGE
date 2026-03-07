# Deploy Mock Lambda with CORS Headers

$REGION = "ap-south-1"
$ROLE_ARN = "arn:aws:iam::150809276128:role/hivemind-lambda-role"

Write-Host "🔧 Deploying Mock Lambda with CORS" -ForegroundColor Cyan
Write-Host ""

# Create ZIP
Write-Host "Creating ZIP..." -ForegroundColor Yellow
Compress-Archive -Path mock-lambda-cors.py -DestinationPath mock-lambda.zip -Force
Write-Host "✅ ZIP created" -ForegroundColor Green

# Deploy mock function
Write-Host ""
Write-Host "Deploying function..." -ForegroundColor Yellow

aws lambda create-function `
    --function-name hivemind-mock-cors `
    --runtime python3.11 `
    --role $ROLE_ARN `
    --handler mock-lambda-cors.handler `
    --zip-file fileb://mock-lambda.zip `
    --timeout 10 `
    --region $REGION 2>$null

if ($LASTEXITCODE -ne 0) {
    # Update if exists
    aws lambda update-function-code `
        --function-name hivemind-mock-cors `
        --zip-file fileb://mock-lambda.zip `
        --region $REGION
}

Write-Host "✅ Function deployed" -ForegroundColor Green

# Update existing Lambda functions to use this code
Write-Host ""
Write-Host "Updating Lambda functions with CORS code..." -ForegroundColor Yellow

$functions = @(
    "hivemind-social-create-brand",
    "hivemind-social-list-brands",
    "hivemind-social-get-brand"
)

foreach ($func in $functions) {
    Write-Host "  → $func" -ForegroundColor Gray
    aws lambda update-function-code `
        --function-name $func `
        --zip-file fileb://mock-lambda.zip `
        --region $REGION `
        --no-cli-pager 2>$null
}

Write-Host ""
Write-Host "✅ All functions updated with CORS support!" -ForegroundColor Green
Write-Host ""
Write-Host "Test it:" -ForegroundColor Yellow
Write-Host "  curl https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod/social/brands" -ForegroundColor Gray
Write-Host ""
Write-Host "Refresh your frontend - CORS errors should be gone!" -ForegroundColor Green

# Cleanup
Remove-Item mock-lambda.zip
