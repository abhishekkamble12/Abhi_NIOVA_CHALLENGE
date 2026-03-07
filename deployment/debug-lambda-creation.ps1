# Debug Lambda Creation

$S3_BUCKET = "media-ai-content"
$REGION = "ap-south-1"
$ACCOUNT_ID = "150809276128"
$ROLE_ARN = "arn:aws:iam::${ACCOUNT_ID}:role/hivemind-lambda-role"
$LAYER_ARN = "arn:aws:lambda:ap-south-1:150809276128:layer:hivemind-layer:1"

Write-Host "Debugging Lambda Creation" -ForegroundColor Cyan
Write-Host ""

# Check S3 files
Write-Host "[1/3] Checking S3 files..." -ForegroundColor Yellow
aws s3 ls s3://$S3_BUCKET/functions/ --region $REGION
Write-Host ""

# Check IAM role
Write-Host "[2/3] Checking IAM role..." -ForegroundColor Yellow
aws iam get-role --role-name hivemind-lambda-role --query 'Role.Arn' --output text
Write-Host ""

# Try creating ONE function with full error output
Write-Host "[3/3] Creating test function..." -ForegroundColor Yellow
Write-Host ""

aws lambda create-function `
    --function-name hivemind-test-function `
    --runtime python3.11 `
    --role $ROLE_ARN `
    --handler handler.handler `
    --code S3Bucket=$S3_BUCKET,S3Key=functions/social_create_brand.zip `
    --timeout 30 `
    --memory-size 512 `
    --layers $LAYER_ARN `
    --environment "Variables={S3_BUCKET=$S3_BUCKET,AWS_REGION=$REGION}" `
    --region $REGION

Write-Host ""
Write-Host "If successful, delete test function:" -ForegroundColor Yellow
Write-Host "  aws lambda delete-function --function-name hivemind-test-function --region ap-south-1" -ForegroundColor Gray
