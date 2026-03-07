# HiveMind Lambda Build & Deployment Script (PowerShell)
# Packages Lambda functions and uploads to S3

param(
    [Parameter(Mandatory=$false)]
    [string]$S3Bucket = $env:S3_DEPLOYMENT_BUCKET,
    
    [Parameter(Mandatory=$false)]
    [string]$Region = $env:AWS_REGION
)

# Configuration
$BUILD_DIR = "build"
$LAYER_DIR = "$BUILD_DIR\layer"
$FUNCTIONS_DIR = "$BUILD_DIR\functions"

if (-not $Region) { $Region = "ap-south-1" }

Write-Host " HiveMind Lambda Build Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Validate S3 bucket
if (-not $S3Bucket) {
    Write-Host " Error: S3_DEPLOYMENT_BUCKET not set" -ForegroundColor Red
    Write-Host "Usage: .\build-lambda.ps1 -S3Bucket your-bucket" -ForegroundColor Yellow
    exit 1
}

# Clean build directory
Write-Host "`n Cleaning build directory..." -ForegroundColor Yellow
if (Test-Path $BUILD_DIR) { Remove-Item -Recurse -Force $BUILD_DIR }
New-Item -ItemType Directory -Path "$LAYER_DIR\python" -Force | Out-Null
New-Item -ItemType Directory -Path $FUNCTIONS_DIR -Force | Out-Null

# Step 1: Build Lambda Layer
Write-Host "`n Building Lambda Layer..." -ForegroundColor Yellow
pip install -r layers\requirements.txt -t "$LAYER_DIR\python" --quiet
pip install psycopg2-binary -t "$LAYER_DIR\python" --quiet

Push-Location $LAYER_DIR
Compress-Archive -Path python -DestinationPath ..\lambda-layer.zip -Force
Pop-Location
Write-Host " Layer packaged: $BUILD_DIR\lambda-layer.zip" -ForegroundColor Green

# Step 2: Package Lambda Functions
Write-Host "`n Packaging Lambda Functions..." -ForegroundColor Yellow

# Copy shared services
New-Item -ItemType Directory -Path "$BUILD_DIR\temp\services" -Force | Out-Null
Copy-Item -Path "services\*.py" -Destination "$BUILD_DIR\temp\services\" -Force
Copy-Item -Path "lambda-microservices\services\*.py" -Destination "$BUILD_DIR\temp\services\" -Force
if (Test-Path "lambda-microservices\shared") {
    Copy-Item -Path "lambda-microservices\shared" -Destination "$BUILD_DIR\temp\" -Recurse -Force
}

# API Gateway Lambda Functions
$FUNCTIONS = @(
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

foreach ($FUNC in $FUNCTIONS) {
    Write-Host "  → Packaging $FUNC..." -ForegroundColor Gray
    $TEMP_DIR = "$BUILD_DIR\temp\$FUNC"
    New-Item -ItemType Directory -Path $TEMP_DIR -Force | Out-Null
    
    # Copy handler
    Copy-Item -Path "lambda-microservices\handlers\${FUNC}.py" -Destination "$TEMP_DIR\handler.py" -Force
    
    # Copy services
    Copy-Item -Path "$BUILD_DIR\temp\services" -Destination $TEMP_DIR -Recurse -Force
    if (Test-Path "$BUILD_DIR\temp\shared") {
        Copy-Item -Path "$BUILD_DIR\temp\shared" -Destination $TEMP_DIR -Recurse -Force
    }
    
    # Create ZIP
    Push-Location $TEMP_DIR
    Compress-Archive -Path * -DestinationPath "..\..\functions\${FUNC}.zip" -Force
    Pop-Location
}

# Step Functions Lambda Functions
$STEPFUNCTIONS = @(
    "stepfunctions_validate_video",
    "stepfunctions_start_transcription",
    "stepfunctions_check_transcription",
    "stepfunctions_detect_scenes",
    "stepfunctions_detect_labels",
    "stepfunctions_check_rekognition",
    "stepfunctions_store_video_results"
)

foreach ($FUNC in $STEPFUNCTIONS) {
    Write-Host "  → Packaging $FUNC..." -ForegroundColor Gray
    $TEMP_DIR = "$BUILD_DIR\temp\$FUNC"
    New-Item -ItemType Directory -Path $TEMP_DIR -Force | Out-Null
    
    # Copy handler
    Copy-Item -Path "lambda-microservices\handlers\${FUNC}.py" -Destination "$TEMP_DIR\handler.py" -Force
    
    # Copy services
    Copy-Item -Path "$BUILD_DIR\temp\services" -Destination $TEMP_DIR -Recurse -Force
    
    # Create ZIP
    Push-Location $TEMP_DIR
    Compress-Archive -Path * -DestinationPath "..\..\functions\${FUNC}.zip" -Force
    Pop-Location
}

Write-Host " Packaged $($FUNCTIONS.Count) API functions + $($STEPFUNCTIONS.Count) Step Functions" -ForegroundColor Green

# Step 3: Upload to S3
Write-Host "`n Uploading to S3..." -ForegroundColor Yellow

# Upload layer
aws s3 cp "$BUILD_DIR\lambda-layer.zip" "s3://$S3Bucket/layers/lambda-layer.zip" --region $Region
Write-Host "    Uploaded lambda-layer.zip" -ForegroundColor Green

# Upload functions
Get-ChildItem "$FUNCTIONS_DIR\*.zip" | ForEach-Object {
    aws s3 cp $_.FullName "s3://$S3Bucket/functions/$($_.Name)" --region $Region
    Write-Host "    Uploaded $($_.Name)" -ForegroundColor Green
}

# Step 4: Generate deployment manifest
Write-Host "`n Generating deployment manifest..." -ForegroundColor Yellow

$manifest = @{
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    region = $Region
    s3_bucket = $S3Bucket
    layer = @{
        name = "hivemind-shared-layer"
        s3_key = "layers/lambda-layer.zip"
        runtime = "python3.11"
    }
    functions = @()
}

foreach ($FUNC in ($FUNCTIONS + $STEPFUNCTIONS)) {
    $manifest.functions += @{
        name = "hivemind-$($FUNC -replace '_','-')"
        handler = "handler.handler"
        s3_key = "functions/${FUNC}.zip"
        runtime = "python3.11"
        timeout = 300
        memory = 512
    }
}

$manifest | ConvertTo-Json -Depth 10 | Out-File "$BUILD_DIR\manifest.json" -Encoding UTF8
aws s3 cp "$BUILD_DIR\manifest.json" "s3://$S3Bucket/manifest.json" --region $Region

# Cleanup temp directory
Remove-Item -Recurse -Force "$BUILD_DIR\temp"

# Summary
Write-Host "`n  Build Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host " Layer: s3://$S3Bucket/layers/lambda-layer.zip" -ForegroundColor White
Write-Host " Functions: s3://$S3Bucket/functions/" -ForegroundColor White
Write-Host " Manifest: s3://$S3Bucket/manifest.json" -ForegroundColor White
Write-Host "`nTotal Functions: $($FUNCTIONS.Count + $STEPFUNCTIONS.Count)" -ForegroundColor White
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Deploy Lambda layer: aws lambda publish-layer-version --layer-name hivemind-shared-layer --content S3Bucket=$S3Bucket,S3Key=layers/lambda-layer.zip" -ForegroundColor Gray
Write-Host "2. Deploy functions using CloudFormation or AWS CLI" -ForegroundColor Gray
Write-Host "3. Configure environment variables for each function" -ForegroundColor Gray
