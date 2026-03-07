# Rebuild Lambda Functions with CORS Support

$S3_BUCKET = "media-ai-content"
$REGION = "ap-south-1"

Write-Host " Rebuilding Lambda Functions with CORS" -ForegroundColor Cyan
Write-Host ""

cd E:\Projects\HiveMind\aws\backend-aws

# Rebuild with proper structure
Write-Host "Rebuilding packages..." -ForegroundColor Yellow
.\build-lambda.ps1 -S3Bucket $S3_BUCKET

Write-Host ""
Write-Host "Packages rebuilt and uploaded to S3" -ForegroundColor Green
Write-Host ""

# Update Lambda functions with new code
Write-Host "Updating Lambda functions..." -ForegroundColor Yellow

$functions = @(
    "social_create_brand",
    "social_get_brand",
    "social_list_brands"
)

foreach ($func in $functions) {
    $functionName = "hivemind-$($func -replace '_','-')"
    Write-Host "  → $functionName" -ForegroundColor Gray
    
    aws lambda update-function-code `
        --function-name $functionName `
        --s3-bucket $S3_BUCKET `
        --s3-key functions/$func.zip `
        --region $REGION `
        --no-cli-pager
    
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host " Lambda functions updated with CORS support!" -ForegroundColor Green
Write-Host ""
Write-Host "Test it:" -ForegroundColor Yellow
Write-Host "  curl https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod/social/brands" -ForegroundColor Gray
Write-Host ""
Write-Host "Refresh your frontend - CORS should work now!" -ForegroundColor Green
