# Deploy Frontend to S3

$S3_BUCKET = "hivemind-frontend-$(Get-Random -Maximum 99999)"
$REGION = "ap-south-1"
$API_URL = "https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod"

Write-Host "🚀 Frontend Deployment" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create S3 bucket
Write-Host "[1/5] Creating S3 bucket..." -ForegroundColor Yellow
aws s3 mb s3://$S3_BUCKET --region $REGION
Write-Host "✅ Bucket created: $S3_BUCKET" -ForegroundColor Green

# Step 2: Upload files
Write-Host ""
Write-Host "[2/5] Uploading files to S3..." -ForegroundColor Yellow
aws s3 sync out/ s3://$S3_BUCKET/ --delete --region $REGION
Write-Host "✅ Files uploaded" -ForegroundColor Green

# Step 3: Enable static website hosting
Write-Host ""
Write-Host "[3/5] Enabling static website hosting..." -ForegroundColor Yellow

@'
{
    "IndexDocument": {
        "Suffix": "index.html"
    },
    "ErrorDocument": {
        "Key": "404.html"
    }
}
'@ | Out-File -FilePath website-config.json -Encoding utf8

aws s3api put-bucket-website `
    --bucket $S3_BUCKET `
    --website-configuration file://website-config.json `
    --region $REGION

Remove-Item website-config.json

Write-Host "✅ Website hosting enabled" -ForegroundColor Green

# Step 4: Set bucket policy for public access
Write-Host ""
Write-Host "[4/5] Setting bucket policy..." -ForegroundColor Yellow

@"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$S3_BUCKET/*"
        }
    ]
}
"@ | Out-File -FilePath bucket-policy.json -Encoding utf8

aws s3api put-bucket-policy `
    --bucket $S3_BUCKET `
    --policy file://bucket-policy.json `
    --region $REGION

Remove-Item bucket-policy.json

Write-Host "✅ Bucket policy set" -ForegroundColor Green

# Step 5: Disable block public access
Write-Host ""
Write-Host "[5/5] Configuring public access..." -ForegroundColor Yellow

aws s3api put-public-access-block `
    --bucket $S3_BUCKET `
    --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" `
    --region $REGION

Write-Host "✅ Public access configured" -ForegroundColor Green

# Get website URL
$WEBSITE_URL = "http://$S3_BUCKET.s3-website.$REGION.amazonaws.com"

Write-Host ""
Write-Host "✅ Frontend Deployed!" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Website URL: $WEBSITE_URL" -ForegroundColor White
Write-Host "S3 Bucket: $S3_BUCKET" -ForegroundColor White
Write-Host "API Endpoint: $API_URL" -ForegroundColor White
Write-Host ""
Write-Host "Open in browser:" -ForegroundColor Yellow
Write-Host "  start $WEBSITE_URL" -ForegroundColor Gray

# Save URLs
@"
WEBSITE_URL=$WEBSITE_URL
S3_BUCKET=$S3_BUCKET
API_URL=$API_URL
"@ | Out-File -FilePath frontend-deployment.txt -Encoding utf8
