# Fix Frontend Bucket Policy

$S3_BUCKET = "hivemind-frontend-83016"
$REGION = "ap-south-1"

Write-Host "🔧 Fixing Frontend Bucket Configuration" -ForegroundColor Cyan
Write-Host ""

# Step 1: Enable static website hosting
Write-Host "[1/2] Enabling static website hosting..." -ForegroundColor Yellow

aws s3api put-bucket-website `
    --bucket $S3_BUCKET `
    --website-configuration '{\"IndexDocument\":{\"Suffix\":\"index.html\"},\"ErrorDocument\":{\"Key\":\"404.html\"}}' `
    --region $REGION

Write-Host "✅ Website hosting enabled" -ForegroundColor Green

# Step 2: Set bucket policy
Write-Host ""
Write-Host "[2/2] Setting bucket policy..." -ForegroundColor Yellow

$policy = "{`"Version`":`"2012-10-17`",`"Statement`":[{`"Sid`":`"PublicReadGetObject`",`"Effect`":`"Allow`",`"Principal`":`"*`",`"Action`":`"s3:GetObject`",`"Resource`":`"arn:aws:s3:::$S3_BUCKET/*`"}]}"

aws s3api put-bucket-policy `
    --bucket $S3_BUCKET `
    --policy $policy `
    --region $REGION

Write-Host "✅ Bucket policy set" -ForegroundColor Green

Write-Host ""
Write-Host "✅ Frontend Fixed!" -ForegroundColor Green
Write-Host ""
Write-Host "Website URL: http://$S3_BUCKET.s3-website.$REGION.amazonaws.com" -ForegroundColor White
Write-Host ""
Write-Host "Test it:" -ForegroundColor Yellow
Write-Host "  start http://$S3_BUCKET.s3-website.$REGION.amazonaws.com" -ForegroundColor Gray
# Fix Frontend Bucket Policy

$S3_BUCKET = "hivemind-frontend-83016"
$REGION = "ap-south-1"

Write-Host "Fixing Frontend Bucket Configuration"
Write-Host ""

# Step 1: Enable static website hosting
Write-Host "[1/2] Enabling static website hosting..."

$websiteConfig = '{
  "IndexDocument": { "Suffix": "index.html" },
  "ErrorDocument": { "Key": "404.html" }
}'

aws s3api put-bucket-website `
    --bucket $S3_BUCKET `
    --website-configuration $websiteConfig `
    --region $REGION

Write-Host "Website hosting enabled"

# Step 2: Set bucket policy
Write-Host ""
Write-Host "[2/2] Setting bucket policy..."

$policy = @"
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
"@

aws s3api put-bucket-policy `
    --bucket $S3_BUCKET `
    --policy $policy `
    --region $REGION

Write-Host "Bucket policy set"
Write-Host ""
Write-Host "Frontend fixed"
Write-Host ""
Write-Host "Website URL: http://$S3_BUCKET.s3-website.$REGION.amazonaws.com"
Write-Host ""
Write-Host "Test it:"
Write-Host "start http://$S3_BUCKET.s3-website.$REGION.amazonaws.com"