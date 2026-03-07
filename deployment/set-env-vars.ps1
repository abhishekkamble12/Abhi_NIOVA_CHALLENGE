# Set Environment Variables for All Lambda Functions

$REGION = "ap-south-1"

Write-Host "⚙️  Setting Lambda Environment Variables" -ForegroundColor Cyan
Write-Host ""

# Environment variables (with placeholders for database)
$envVars = @{
    DB_HOST = "PLACEHOLDER_AURORA_ENDPOINT"
    DB_PORT = "5432"
    DB_NAME = "hiveminddb"
    DB_USER = "hivemind"
    DB_PASSWORD = "PLACEHOLDER_PASSWORD"
    S3_BUCKET = "media-ai-content"
    AWS_REGION = "ap-south-1"
}

# Convert to JSON format for AWS CLI
$envJson = $envVars | ConvertTo-Json -Compress
$envString = "Variables=$envJson"

Write-Host "Environment Variables:" -ForegroundColor Yellow
$envVars | Format-Table -AutoSize

Write-Host ""
Write-Host "Updating functions..." -ForegroundColor Yellow

$functions = @(
    "hivemind-social-create-brand",
    "hivemind-social-get-brand",
    "hivemind-social-list-brands",
    "hivemind-social-get-post",
    "hivemind-social-generate-content",
    "hivemind-feed-personalized",
    "hivemind-video-upload-handler",
    "hivemind-ai-generate-content",
    "hivemind-ai-process-video",
    "hivemind-stepfunctions-validate-video",
    "hivemind-stepfunctions-start-transcription",
    "hivemind-stepfunctions-check-transcription",
    "hivemind-stepfunctions-detect-scenes",
    "hivemind-stepfunctions-detect-labels",
    "hivemind-stepfunctions-check-rekognition",
    "hivemind-stepfunctions-store-video-results"
)

foreach ($func in $functions) {
    Write-Host "  → $func" -ForegroundColor Gray
    
    aws lambda update-function-configuration `
        --function-name $func `
        --environment "Variables={DB_HOST=PLACEHOLDER,DB_PORT=5432,DB_NAME=hiveminddb,DB_USER=hivemind,DB_PASSWORD=PLACEHOLDER,S3_BUCKET=media-ai-content,AWS_REGION=ap-south-1}" `
        --region $REGION `
        --no-cli-pager 2>$null
    
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "✅ Environment variables set for all functions" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Note: Database credentials are placeholders" -ForegroundColor Yellow
Write-Host "   Update them after deploying Aurora PostgreSQL" -ForegroundColor Yellow
