# Quick Fix: Create IAM Role and Update Lambda Functions

$ROLE_NAME = "hivemind-lambda-execution-role"
$REGION = "ap-south-1"
$ACCOUNT_ID = "150809276128"

Write-Host "🔧 Quick Fix: IAM Role Setup" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create IAM Role
Write-Host "[1/3] Creating IAM Role..." -ForegroundColor Yellow

aws iam create-role `
    --role-name $ROLE_NAME `
    --assume-role-policy-document '{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"lambda.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}' `
    2>$null

aws iam attach-role-policy `
    --role-name $ROLE_NAME `
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

@'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:*"],
      "Resource": ["arn:aws:s3:::media-ai-content/*", "arn:aws:s3:::media-ai-content"]
    },
    {
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel"],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": ["transcribe:*", "rekognition:*"],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": ["dynamodb:*"],
      "Resource": "arn:aws:dynamodb:ap-south-1:*:table/hivemind-*"
    }
  ]
}
'@ | Out-File -FilePath lambda-policy.json -Encoding utf8

aws iam put-role-policy `
    --role-name $ROLE_NAME `
    --policy-name hivemind-lambda-policy `
    --policy-document file://lambda-policy.json

$ROLE_ARN = aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text
Write-Host "✅ Role created: $ROLE_ARN" -ForegroundColor Green
$ROLE_ARN | Out-File role-arn.txt

# Step 2: Wait for IAM propagation
Write-Host ""
Write-Host "[2/3] Waiting for IAM propagation..." -ForegroundColor Yellow
Start-Sleep -Seconds 15
Write-Host "✅ Ready" -ForegroundColor Green

# Step 3: Update Lambda functions
Write-Host ""
Write-Host "[3/3] Updating Lambda Functions..." -ForegroundColor Yellow

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
        --role $ROLE_ARN `
        --region $REGION `
        --no-cli-pager 2>$null
    Start-Sleep -Seconds 1
}

Write-Host "✅ All functions updated" -ForegroundColor Green

# Step 4: Grant API Gateway permissions
Write-Host ""
Write-Host "[4/4] Granting API Gateway Permissions..." -ForegroundColor Yellow

$API_ID = "wcp5c3ga8b"

aws lambda add-permission `
    --function-name hivemind-social-create-brand `
    --statement-id apigateway-invoke-1 `
    --action lambda:InvokeFunction `
    --principal apigateway.amazonaws.com `
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*" `
    2>$null

aws lambda add-permission `
    --function-name hivemind-social-list-brands `
    --statement-id apigateway-invoke-2 `
    --action lambda:InvokeFunction `
    --principal apigateway.amazonaws.com `
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*" `
    2>$null

aws lambda add-permission `
    --function-name hivemind-social-get-brand `
    --statement-id apigateway-invoke-3 `
    --action lambda:InvokeFunction `
    --principal apigateway.amazonaws.com `
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*" `
    2>$null

Write-Host "✅ Permissions granted" -ForegroundColor Green

# Cleanup
Remove-Item lambda-policy.json -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "API URL: https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod" -ForegroundColor White
Write-Host ""
Write-Host "Test with:" -ForegroundColor Yellow
Write-Host "  curl https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod/social/brands" -ForegroundColor Gray
