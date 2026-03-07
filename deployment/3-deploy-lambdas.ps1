# Deploy All Lambda Functions from S3

$S3_BUCKET = "media-ai-content"
$REGION = "ap-south-1"
$ACCOUNT_ID = "586098609294"

# Read ARNs from previous steps
$LAYER_ARN = Get-Content "layer-arn.txt"
$ROLE_ARN = Get-Content "role-arn.txt"

Write-Host "🚀 Deploying Lambda Functions..." -ForegroundColor Cyan

# Environment variables template
$envVars = "Variables={DB_HOST=PLACEHOLDER,DB_PORT=5432,DB_NAME=hiveminddb,DB_USER=hivemind,DB_PASSWORD=PLACEHOLDER,S3_BUCKET=media-ai-content,AWS_REGION=ap-south-1}"

# API Gateway Functions
$apiFunctions = @(
    "social_create_brand",
    "social_get_brand",
    "social_list_brands",
    "social_get_post",
    "social_generate_content",
    "feed_personalized",
    "video_upload_handler",
    "ai_generate_content",
    "ai_process_video"
)

# Step Functions
$stepFunctions = @(
    "stepfunctions_validate_video",
    "stepfunctions_start_transcription",
    "stepfunctions_check_transcription",
    "stepfunctions_detect_scenes",
    "stepfunctions_detect_labels",
    "stepfunctions_check_rekognition",
    "stepfunctions_store_video_results"
)

$allFunctions = $apiFunctions + $stepFunctions

foreach ($func in $allFunctions) {
    $functionName = "hivemind-$($func -replace '_','-')"
    $s3Key = "functions/$func.zip"
    
    Write-Host "  → Creating $functionName..." -ForegroundColor Gray
    
    aws lambda create-function `
        --function-name $functionName `
        --runtime python3.11 `
        --role $ROLE_ARN `
        --handler handler.handler `
        --code S3Bucket=$S3_BUCKET,S3Key=$s3Key `
        --timeout 300 `
        --memory-size 512 `
        --layers $LAYER_ARN `
        --environment $envVars `
        --region $REGION `
        --no-cli-pager 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    ✅ $functionName created" -ForegroundColor Green
    } else {
        Write-Host "    ⚠️  $functionName may already exist" -ForegroundColor Yellow
    }
}

Write-Host "`n✅ All Lambda functions deployed!" -ForegroundColor Green
Write-Host "Total functions: $($allFunctions.Count)" -ForegroundColor White
