# Deploy Lambda Layer from S3

$LAYER_NAME = "hivemind-shared-layer"
$S3_BUCKET = "media-ai-content"
$S3_KEY = "layers/lambda-layer.zip"
$REGION = "ap-south-1"

Write-Host "📦 Deploying Lambda Layer..." -ForegroundColor Cyan

$LAYER_ARN = aws lambda publish-layer-version `
    --layer-name $LAYER_NAME `
    --content S3Bucket=$S3_BUCKET,S3Key=$S3_KEY `
    --compatible-runtimes python3.11 `
    --region $REGION `
    --query 'LayerVersionArn' `
    --output text

Write-Host "✅ Layer deployed: $LAYER_ARN" -ForegroundColor Green
Set-Content -Path "layer-arn.txt" -Value $LAYER_ARN
