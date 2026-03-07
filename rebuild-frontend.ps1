# Rebuild and Redeploy Frontend with API Gateway URL

$API_URL = "https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod"
$S3_BUCKET = "hivemind-frontend-83016"
$REGION = "ap-south-1"

Write-Host "Rebuilding Frontend with API Gateway" -ForegroundColor Cyan
Write-Host ""

# Step 1: Set environment variable
Write-Host "[1/4] Setting API URL..." -ForegroundColor Yellow
"NEXT_PUBLIC_API_URL=$API_URL" | Out-File -FilePath .env.production -Encoding utf8
Write-Host " API URL: $API_URL" -ForegroundColor Green

# Step 2: Rebuild Next.js
Write-Host ""
Write-Host "[2/4] Building Next.js..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Build failed" -ForegroundColor Red
    exit 1
}
Write-Host "  Build complete" -ForegroundColor Green

# Step 3: Upload to S3
Write-Host ""
Write-Host "[3/4] Uploading to S3..." -ForegroundColor Yellow
aws s3 sync out/ s3://$S3_BUCKET/ --delete --region $REGION
Write-Host "  Files uploaded" -ForegroundColor Green

# Step 4: Verify
Write-Host ""
Write-Host "[4/4] Verifying deployment..." -ForegroundColor Yellow
$indexContent = aws s3 cp s3://$S3_BUCKET/index.html - --region $REGION

if ($indexContent -match $API_URL) {
    Write-Host "  API URL found in deployed files" -ForegroundColor Green
} else {
    Write-Host "  API URL not found - check build" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Frontend Redeployed!" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Website: http://$S3_BUCKET.s3-website.$REGION.amazonaws.com" -ForegroundColor White
Write-Host "API: $API_URL" -ForegroundColor White
Write-Host ""
Write-Host "Open browser and check console for API endpoint:" -ForegroundColor Yellow
Write-Host "  start http://$S3_BUCKET.s3-website.$REGION.amazonaws.com" -ForegroundColor Gray
Write-Host ""
Write-Host "You should see:  API Endpoint: $API_URL" -ForegroundColor Gray
