# HiveMind Frontend Build & Deployment Script (PowerShell)
# Builds Next.js and deploys to S3 + CloudFront

param(
    [Parameter(Mandatory=$false)]
    [string]$S3Bucket = $env:S3_FRONTEND_BUCKET,
    
    [Parameter(Mandatory=$false)]
    [string]$ApiUrl = $env:NEXT_PUBLIC_API_URL,
    
    [Parameter(Mandatory=$false)]
    [string]$Region = $env:AWS_REGION,
    
    [Parameter(Mandatory=$false)]
    [string]$CloudFrontId = $env:CLOUDFRONT_DISTRIBUTION_ID
)

if (-not $Region) { $Region = "ap-south-1" }

Write-Host "🚀 HiveMind Frontend Build & Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Validate parameters
if (-not $S3Bucket) {
    Write-Host "❌ Error: S3_FRONTEND_BUCKET not set" -ForegroundColor Red
    Write-Host "Usage: .\build-frontend.ps1 -S3Bucket your-bucket -ApiUrl https://api.example.com" -ForegroundColor Yellow
    exit 1
}

if (-not $ApiUrl) {
    Write-Host "⚠️  Warning: NEXT_PUBLIC_API_URL not set, using placeholder" -ForegroundColor Yellow
    $ApiUrl = "https://api-placeholder.execute-api.ap-south-1.amazonaws.com/prod"
}

# Step 1: Set environment variables
Write-Host "`n📝 Configuring environment..." -ForegroundColor Yellow
$envContent = "NEXT_PUBLIC_API_URL=$ApiUrl"
Set-Content -Path ".env.production" -Value $envContent
Write-Host "  ✅ Created .env.production" -ForegroundColor Green

# Step 2: Install dependencies
Write-Host "`n📦 Installing dependencies..." -ForegroundColor Yellow
npm install --silent
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ npm install failed" -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Dependencies installed" -ForegroundColor Green

# Step 3: Build Next.js
Write-Host "`n🔨 Building Next.js application..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Build complete" -ForegroundColor Green

# Step 4: Verify output directory
if (-not (Test-Path "out")) {
    Write-Host "❌ Error: out/ directory not found" -ForegroundColor Red
    exit 1
}

$fileCount = (Get-ChildItem -Path "out" -Recurse -File).Count
Write-Host "  📄 Generated $fileCount files" -ForegroundColor Gray

# Step 5: Upload to S3
Write-Host "`n☁️  Uploading to S3..." -ForegroundColor Yellow

# Sync files to S3
aws s3 sync out/ "s3://$S3Bucket/" `
    --delete `
    --cache-control "public, max-age=31536000, immutable" `
    --exclude "*.html" `
    --region $Region

# Upload HTML files with different cache settings
aws s3 sync out/ "s3://$S3Bucket/" `
    --exclude "*" `
    --include "*.html" `
    --cache-control "public, max-age=0, must-revalidate" `
    --region $Region

Write-Host "  ✅ Files uploaded to s3://$S3Bucket/" -ForegroundColor Green

# Step 6: Set bucket website configuration
Write-Host "`n🌐 Configuring S3 website hosting..." -ForegroundColor Yellow

$websiteConfig = @"
{
    "IndexDocument": {
        "Suffix": "index.html"
    },
    "ErrorDocument": {
        "Key": "404.html"
    }
}
"@

Set-Content -Path "website-config.json" -Value $websiteConfig
aws s3api put-bucket-website `
    --bucket $S3Bucket `
    --website-configuration file://website-config.json `
    --region $Region
Remove-Item "website-config.json"

Write-Host "  ✅ Website hosting configured" -ForegroundColor Green

# Step 7: Invalidate CloudFront (if distribution ID provided)
if ($CloudFrontId) {
    Write-Host "`n🔄 Invalidating CloudFront cache..." -ForegroundColor Yellow
    
    $invalidationId = aws cloudfront create-invalidation `
        --distribution-id $CloudFrontId `
        --paths "/*" `
        --query 'Invalidation.Id' `
        --output text
    
    Write-Host "  ✅ Invalidation created: $invalidationId" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Skipping CloudFront invalidation (no distribution ID)" -ForegroundColor Yellow
}

# Step 8: Get website URL
Write-Host "`n📊 Deployment Summary" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan

$websiteUrl = "http://$S3Bucket.s3-website.$Region.amazonaws.com"
Write-Host "S3 Website URL: $websiteUrl" -ForegroundColor White

if ($CloudFrontId) {
    $cfDomain = aws cloudfront get-distribution `
        --id $CloudFrontId `
        --query 'Distribution.DomainName' `
        --output text 2>$null
    
    if ($cfDomain) {
        Write-Host "CloudFront URL: https://$cfDomain" -ForegroundColor White
    }
}

Write-Host "`nAPI Endpoint: $ApiUrl" -ForegroundColor White
Write-Host "Files Deployed: $fileCount" -ForegroundColor White

Write-Host "`n✅ Deployment Complete!" -ForegroundColor Green
