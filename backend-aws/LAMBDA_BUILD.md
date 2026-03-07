# Lambda Build & Deployment

Automated build scripts for packaging and deploying HiveMind Lambda functions.

## Prerequisites

- Python 3.11
- AWS CLI configured
- S3 bucket for deployment artifacts

## Quick Start

### Linux/macOS

```bash
# Set S3 bucket
export S3_DEPLOYMENT_BUCKET=your-deployment-bucket

# Run build script
cd backend-aws
chmod +x build-lambda.sh
./build-lambda.sh
```

### Windows

```powershell
# Run build script
cd backend-aws
.\build-lambda.ps1 -S3Bucket your-deployment-bucket
```

## What It Does

1. **Installs Dependencies** - Packages Python libraries into Lambda layer
2. **Packages Functions** - Creates individual ZIP files for each Lambda
3. **Creates Layer** - Bundles shared dependencies (boto3, psycopg2)
4. **Uploads to S3** - Deploys all artifacts to S3 bucket
5. **Generates Manifest** - Creates deployment metadata JSON

## Output Structure

```
build/
├── lambda-layer.zip              # Shared Lambda layer
├── functions/
│   ├── social_create_brand.zip
│   ├── social_get_brand.zip
│   ├── social_list_brands.zip
│   ├── social_get_post.zip
│   ├── social_generate_content.zip
│   ├── feed_personalized.zip
│   ├── video_upload_handler.zip
│   ├── ai_generate_content.zip
│   ├── ai_process_video.zip
│   ├── stepfunctions_validate_video.zip
│   ├── stepfunctions_start_transcription.zip
│   ├── stepfunctions_check_transcription.zip
│   ├── stepfunctions_detect_scenes.zip
│   ├── stepfunctions_detect_labels.zip
│   ├── stepfunctions_check_rekognition.zip
│   └── stepfunctions_store_video_results.zip
└── manifest.json                 # Deployment metadata
```

## S3 Structure

```
s3://your-bucket/
├── layers/
│   └── lambda-layer.zip
├── functions/
│   ├── social_create_brand.zip
│   └── ... (all function ZIPs)
└── manifest.json
```

## Lambda Layer Contents

- boto3 >= 1.34.0
- botocore >= 1.34.0
- psycopg2-binary (PostgreSQL driver)

## Function Packaging

Each Lambda ZIP includes:
- `handler.py` - Lambda entrypoint
- `services/` - Database and AI service modules
- `shared/` - Utility functions

## Deploy Lambda Layer

```bash
aws lambda publish-layer-version \
  --layer-name hivemind-shared-layer \
  --content S3Bucket=your-bucket,S3Key=layers/lambda-layer.zip \
  --compatible-runtimes python3.11 \
  --region ap-south-1
```

## Deploy Functions (Example)

```bash
# Get layer ARN
LAYER_ARN=$(aws lambda list-layer-versions \
  --layer-name hivemind-shared-layer \
  --query 'LayerVersions[0].LayerVersionArn' \
  --output text)

# Create function
aws lambda create-function \
  --function-name hivemind-social-create-brand \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT:role/lambda-role \
  --handler handler.handler \
  --code S3Bucket=your-bucket,S3Key=functions/social_create_brand.zip \
  --layers $LAYER_ARN \
  --timeout 30 \
  --memory-size 512
```

## Update Existing Functions

```bash
# Update function code
aws lambda update-function-code \
  --function-name hivemind-social-create-brand \
  --s3-bucket your-bucket \
  --s3-key functions/social_create_brand.zip
```

## Environment Variables

All Lambda functions require:

```bash
DB_HOST=<aurora-endpoint>
DB_PORT=5432
DB_NAME=hiveminddb
DB_USER=hivemind
DB_PASSWORD=<password>
S3_BUCKET=<media-bucket>
OPENSEARCH_ENDPOINT=<opensearch-endpoint>
AWS_REGION=ap-south-1
```

## Troubleshooting

### Import Errors

Ensure Lambda layer is attached:
```bash
aws lambda get-function-configuration \
  --function-name hivemind-social-create-brand \
  --query 'Layers'
```

### ZIP Too Large

Lambda deployment package limit: 50MB (zipped), 250MB (unzipped)

If exceeded:
1. Remove unnecessary dependencies
2. Use Lambda layers for large libraries
3. Store large files in S3

### Handler Not Found

Verify handler path matches: `handler.handler`
- File: `handler.py`
- Function: `def handler(event, context)`

## CI/CD Integration

### GitHub Actions

```yaml
- name: Build Lambda
  run: |
    cd backend-aws
    ./build-lambda.sh
  env:
    S3_DEPLOYMENT_BUCKET: ${{ secrets.S3_BUCKET }}
    AWS_REGION: ap-south-1
```

### AWS CodeBuild

```yaml
phases:
  build:
    commands:
      - cd backend-aws
      - chmod +x build-lambda.sh
      - ./build-lambda.sh
```

## Manifest Schema

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "region": "ap-south-1",
  "s3_bucket": "deployment-bucket",
  "layer": {
    "name": "hivemind-shared-layer",
    "s3_key": "layers/lambda-layer.zip",
    "runtime": "python3.11"
  },
  "functions": [
    {
      "name": "hivemind-social-create-brand",
      "handler": "handler.handler",
      "s3_key": "functions/social_create_brand.zip",
      "runtime": "python3.11",
      "timeout": 300,
      "memory": 512
    }
  ]
}
```

## Clean Build

```bash
# Remove build artifacts
rm -rf build/

# Re-run build
./build-lambda.sh
```
