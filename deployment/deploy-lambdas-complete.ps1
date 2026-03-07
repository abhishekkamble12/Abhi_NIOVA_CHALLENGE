# Complete Lambda Deployment - Creates Everything

$S3_BUCKET = "media-ai-content"
$REGION = "ap-south-1"
$ACCOUNT_ID = "150809276128"

Write-Host " Complete Lambda Deployment" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create IAM Role
Write-Host "[1/4] Creating IAM Role..." -ForegroundColor Yellow

$trustPolicy = @'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
'@

$trustPolicy | Out-File trust-policy.json -Encoding utf8

aws iam create-role `
    --role-name hivemind-lambda-role `
    --assume-role-policy-document file://trust-policy.json `
    --region $REGION 2>$null

aws iam attach-role-policy `
    --role-name hivemind-lambda-role `
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

$ROLE_ARN = "arn:aws:iam::${ACCOUNT_ID}:role/hivemind-lambda-role"
Write-Host "Role: $ROLE_ARN" -ForegroundColor Green

Remove-Item trust-policy.json

# Wait for IAM propagation
Write-Host " Waiting 15 seconds for IAM..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Step 2: Deploy Lambda Layer
Write-Host ""
Write-Host "[2/4] Deploying Lambda Layer..." -ForegroundColor Yellow

$LAYER_ARN = aws lambda publish-layer-version `
    --layer-name hivemind-layer `
    --content S3Bucket=$S3_BUCKET,S3Key=layers/lambda-layer.zip `
    --compatible-runtimes python3.11 `
    --region $REGION `
    --query 'LayerVersionArn' `
    --output text

Write-Host " Layer: $LAYER_ARN" -ForegroundColor Green

# Step 3: Create Lambda Functions
Write-Host ""
Write-Host "[3/4] Creating Lambda Functions..." -ForegroundColor Yellow

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

$count = 0
foreach ($func in $functions) {
    $functionName = "hivemind-$($func -replace '_','-')"
    Write-Host "  → $functionName" -ForegroundColor Gray
    
    aws lambda create-function `
        --function-name $functionName `
        --runtime python3.11 `
        --role $ROLE_ARN `
        --handler handler.handler `
        --code S3Bucket=$S3_BUCKET,S3Key=functions/$func.zip `
        --timeout 30 `
        --memory-size 512 `
        --layers $LAYER_ARN `
        --environment "Variables={S3_BUCKET=$S3_BUCKET,AWS_REGION=$REGION}" `
        --region $REGION `
        --no-cli-pager 2>$null
    
    if ($LASTEXITCODE -eq 0) { $count++ }
    Start-Sleep -Seconds 2
}

Write-Host " Created $count functions" -ForegroundColor Green

# Step 4: Grant API Gateway Permissions
Write-Host ""
Write-Host "[4/4] Granting API Gateway Permissions..." -ForegroundColor Yellow

$API_ID = "wcp5c3ga8b"

$apiFunctions = @(
    "hivemind-social-create-brand",
    "hivemind-social-list-brands",
    "hivemind-social-get-brand"
)

foreach ($func in $apiFunctions) {
    aws lambda add-permission `
        --function-name $func `
        --statement-id apigateway-invoke `
        --action lambda:InvokeFunction `
        --principal apigateway.amazonaws.com `
        --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*" `
        --region $REGION 2>$null
}

Write-Host " Permissions granted" -ForegroundColor Green

Write-Host ""
Write-Host " Deployment Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Verify:" -ForegroundColor Yellow
Write-Host "  aws lambda list-functions --query 'Functions[?starts_with(FunctionName, ``hivemind-``)].FunctionName' --region ap-south-1" -ForegroundColor Gray
