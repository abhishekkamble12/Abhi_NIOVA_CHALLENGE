#!/bin/bash
set -e

# HiveMind Lambda Build & Deployment Script
# Packages Lambda functions and uploads to S3

# Configuration
BUILD_DIR="build"
LAYER_DIR="$BUILD_DIR/layer"
FUNCTIONS_DIR="$BUILD_DIR/functions"
S3_BUCKET="${S3_DEPLOYMENT_BUCKET:-hivemind-deployment}"
REGION="${AWS_REGION:-ap-south-1}"

echo "🚀 HiveMind Lambda Build Script"
echo "================================"

# Validate S3 bucket
if [ -z "$S3_DEPLOYMENT_BUCKET" ]; then
    echo "❌ Error: S3_DEPLOYMENT_BUCKET environment variable not set"
    echo "Usage: S3_DEPLOYMENT_BUCKET=your-bucket ./build-lambda.sh"
    exit 1
fi

# Clean build directory
echo "🧹 Cleaning build directory..."
rm -rf $BUILD_DIR
mkdir -p $LAYER_DIR/python
mkdir -p $FUNCTIONS_DIR

# Step 1: Build Lambda Layer
echo ""
echo "📦 Building Lambda Layer..."
pip install -r layers/requirements.txt -t $LAYER_DIR/python/ --quiet
pip install psycopg2-binary -t $LAYER_DIR/python/ --quiet

cd $LAYER_DIR
zip -r ../lambda-layer.zip python/ > /dev/null
cd ../..
echo "✅ Layer packaged: $BUILD_DIR/lambda-layer.zip"

# Step 2: Package Lambda Functions
echo ""
echo "📦 Packaging Lambda Functions..."

# Copy shared services
mkdir -p $BUILD_DIR/temp/services
cp -r services/*.py $BUILD_DIR/temp/services/
cp -r lambda-microservices/services/*.py $BUILD_DIR/temp/services/
cp -r lambda-microservices/shared $BUILD_DIR/temp/

# API Gateway Lambda Functions
FUNCTIONS=(
    "social_create_brand"
    "social_get_brand"
    "social_list_brands"
    "social_get_post"
    "social_generate_content"
    "feed_personalized"
    "video_upload_handler"
    "ai_generate_content"
    "ai_process_video"
)

for FUNC in "${FUNCTIONS[@]}"; do
    echo "  → Packaging $FUNC..."
    TEMP_DIR="$BUILD_DIR/temp/$FUNC"
    mkdir -p $TEMP_DIR
    
    # Copy handler
    cp lambda-microservices/handlers/${FUNC}.py $TEMP_DIR/handler.py
    
    # Copy services
    cp -r $BUILD_DIR/temp/services $TEMP_DIR/
    cp -r $BUILD_DIR/temp/shared $TEMP_DIR/ 2>/dev/null || true
    
    # Create ZIP
    cd $TEMP_DIR
    zip -r ../../../$FUNCTIONS_DIR/${FUNC}.zip . > /dev/null
    cd ../../..
done

# Step Functions Lambda Functions
STEPFUNCTIONS=(
    "stepfunctions_validate_video"
    "stepfunctions_start_transcription"
    "stepfunctions_check_transcription"
    "stepfunctions_detect_scenes"
    "stepfunctions_detect_labels"
    "stepfunctions_check_rekognition"
    "stepfunctions_store_video_results"
)

for FUNC in "${STEPFUNCTIONS[@]}"; do
    echo "  → Packaging $FUNC..."
    TEMP_DIR="$BUILD_DIR/temp/$FUNC"
    mkdir -p $TEMP_DIR
    
    # Copy handler
    cp lambda-microservices/handlers/${FUNC}.py $TEMP_DIR/handler.py
    
    # Copy services
    cp -r $BUILD_DIR/temp/services $TEMP_DIR/
    
    # Create ZIP
    cd $TEMP_DIR
    zip -r ../../../$FUNCTIONS_DIR/${FUNC}.zip . > /dev/null
    cd ../../..
done

echo "✅ Packaged ${#FUNCTIONS[@]} API functions + ${#STEPFUNCTIONS[@]} Step Functions"

# Step 3: Upload to S3
echo ""
echo "☁️  Uploading to S3..."

# Upload layer
aws s3 cp $BUILD_DIR/lambda-layer.zip s3://$S3_BUCKET/layers/lambda-layer.zip --region $REGION
echo "  ✅ Uploaded lambda-layer.zip"

# Upload functions
for ZIP in $FUNCTIONS_DIR/*.zip; do
    FILENAME=$(basename $ZIP)
    aws s3 cp $ZIP s3://$S3_BUCKET/functions/$FILENAME --region $REGION
    echo "  ✅ Uploaded $FILENAME"
done

# Step 4: Generate deployment manifest
echo ""
echo "📝 Generating deployment manifest..."
cat > $BUILD_DIR/manifest.json <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "region": "$REGION",
  "s3_bucket": "$S3_BUCKET",
  "layer": {
    "name": "hivemind-shared-layer",
    "s3_key": "layers/lambda-layer.zip",
    "runtime": "python3.11"
  },
  "functions": [
EOF

FIRST=true
for FUNC in "${FUNCTIONS[@]}" "${STEPFUNCTIONS[@]}"; do
    if [ "$FIRST" = true ]; then
        FIRST=false
    else
        echo "," >> $BUILD_DIR/manifest.json
    fi
    cat >> $BUILD_DIR/manifest.json <<EOF
    {
      "name": "hivemind-${FUNC//_/-}",
      "handler": "handler.handler",
      "s3_key": "functions/${FUNC}.zip",
      "runtime": "python3.11",
      "timeout": 300,
      "memory": 512
    }
EOF
done

cat >> $BUILD_DIR/manifest.json <<EOF

  ]
}
EOF

aws s3 cp $BUILD_DIR/manifest.json s3://$S3_BUCKET/manifest.json --region $REGION

# Cleanup temp directory
rm -rf $BUILD_DIR/temp

# Summary
echo ""
echo "✅ Build Complete!"
echo "================================"
echo "📦 Layer: s3://$S3_BUCKET/layers/lambda-layer.zip"
echo "📦 Functions: s3://$S3_BUCKET/functions/"
echo "📄 Manifest: s3://$S3_BUCKET/manifest.json"
echo ""
echo "Total Functions: $((${#FUNCTIONS[@]} + ${#STEPFUNCTIONS[@]}))"
echo ""
echo "Next Steps:"
echo "1. Deploy Lambda layer: aws lambda publish-layer-version --layer-name hivemind-shared-layer --content S3Bucket=$S3_BUCKET,S3Key=layers/lambda-layer.zip"
echo "2. Deploy functions using CloudFormation or AWS CLI"
echo "3. Configure environment variables for each function"
