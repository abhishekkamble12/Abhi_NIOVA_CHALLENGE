# Debug Lambda Function Issues

$FUNCTION_NAME = "hivemind-social-list-brands"
$REGION = "ap-south-1"

Write-Host "🔍 Debugging Lambda Function: $FUNCTION_NAME" -ForegroundColor Cyan
Write-Host ""

# Check function configuration
Write-Host "[1/4] Checking Function Configuration..." -ForegroundColor Yellow
aws lambda get-function-configuration --function-name $FUNCTION_NAME --region $REGION

Write-Host ""
Write-Host "[2/4] Checking Recent Logs..." -ForegroundColor Yellow
$LOG_GROUP = "/aws/lambda/$FUNCTION_NAME"

# Get latest log stream
$LATEST_STREAM = aws logs describe-log-streams `
    --log-group-name $LOG_GROUP `
    --order-by LastEventTime `
    --descending `
    --max-items 1 `
    --query 'logStreams[0].logStreamName' `
    --output text `
    --region $REGION 2>$null

if ($LATEST_STREAM) {
    Write-Host "Latest log stream: $LATEST_STREAM" -ForegroundColor Gray
    Write-Host ""
    
    # Get logs
    aws logs get-log-events `
        --log-group-name $LOG_GROUP `
        --log-stream-name $LATEST_STREAM `
        --limit 50 `
        --region $REGION `
        --query 'events[*].message' `
        --output text
} else {
    Write-Host "⚠️  No logs found. Function may not have been invoked yet." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3/4] Testing Function Directly..." -ForegroundColor Yellow

# Create test event
$testEvent = @'
{
  "httpMethod": "GET",
  "path": "/social/brands",
  "headers": {},
  "queryStringParameters": null,
  "body": null
}
'@

$testEvent | Out-File -FilePath test-event.json -Encoding utf8

# Invoke function
Write-Host "Invoking function..." -ForegroundColor Gray
aws lambda invoke `
    --function-name $FUNCTION_NAME `
    --payload file://test-event.json `
    --region $REGION `
    response.json

Write-Host ""
Write-Host "Response:" -ForegroundColor Gray
Get-Content response.json

Write-Host ""
Write-Host "[4/4] Common Issues & Fixes:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Issue 1: Missing database_service module" -ForegroundColor Red
Write-Host "  Fix: Ensure services/ folder is in Lambda ZIP" -ForegroundColor Green
Write-Host ""
Write-Host "Issue 2: Database connection error" -ForegroundColor Red
Write-Host "  Fix: Set DB_HOST environment variable" -ForegroundColor Green
Write-Host ""
Write-Host "Issue 3: Handler not found" -ForegroundColor Red
Write-Host "  Fix: Verify handler.handler exists in ZIP" -ForegroundColor Green
Write-Host ""

# Cleanup
Remove-Item test-event.json, response.json -ErrorAction SilentlyContinue
