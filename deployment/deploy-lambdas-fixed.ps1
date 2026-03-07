# Deploy Lambda Functions - FIXED

$S3_BUCKET = "media-ai-content"
$REGION = "ap-south-1"
$ACCOUNT_ID = "150809276128"
$ROLE_ARN = "arn:aws:iam::${ACCOUNT_ID}:role/hivemind-lambda-role"
$LAYER_ARN = "arn:aws:lambda:ap-south-1:150809276128:layer:hivemind-layer:1"

Write-Host " Deploying Lambda Functions" -ForegroundColor Cyan
Write-Host ""

$functions = @(
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

$created = 0
foreach ($func in $functions) {
    $functionName = "hivemind-$($func -replace '_','-')"
    Write-Host "Creating $functionName..." -ForegroundColor Yellow
    
    $result = aws lambda create-function `
        --function-name $functionName `
        --runtime python3.11 `
        --role $ROLE_ARN `
        --handler handler.handler `
        --code S3Bucket=$S3_BUCKET,S3Key=functions/$func.zip `
        --timeout 30 `
        --memory-size 512 `
        --layers $LAYER_ARN `
        --environment "Variables={S3_BUCKET=$S3_BUCKET,DB_HOST=PLACEHOLDER,DB_PORT=5432,DB_NAME=hiveminddb,DB_USER=hivemind,DB_PASSWORD=PLACEHOLDER}" `
        --region $REGION `
        2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Created" -ForegroundColor Green
        $created++
    } else {
        Write-Host "   Failed: $result" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host " Created $created/$($functions.Count) functions" -ForegroundColor Green
Write-Host ""

# Grant API Gateway permissions
Write-Host "Granting API Gateway permissions..." -ForegroundColor Yellow
$API_ID = "wcp5c3ga8b"

$apiFunctions = @("hivemind-social-create-brand", "hivemind-social-list-brands", "hivemind-social-get-brand")

foreach ($func in $apiFunctions) {
    aws lambda add-permission `
        --function-name $func `
        --statement-id apigateway-$(Get-Random) `
        --action lambda:InvokeFunction `
        --principal apigateway.amazonaws.com `
        --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*" `
        --region $REGION 2>$null
}

Write-Host " Permissions granted" -ForegroundColor Green
Write-Host ""
Write-Host "Verify:" -ForegroundColor Yellow
Write-Host "  aws lambda list-functions --query 'Functions[?starts_with(FunctionName, ``hivemind-``)].FunctionName' --region ap-south-1" -ForegroundColor Gray
