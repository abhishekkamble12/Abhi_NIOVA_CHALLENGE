# Create IAM Role for Lambda Execution

$ROLE_NAME = "hivemind-lambda-execution-role"
$REGION = "ap-south-1"

Write-Host "🔐 Creating IAM Role..." -ForegroundColor Cyan

# Trust policy
$trustPolicy = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
"@

Set-Content -Path "trust-policy.json" -Value $trustPolicy

# Create role
aws iam create-role `
  --role-name $ROLE_NAME `
  --assume-role-policy-document file://trust-policy.json

# Attach basic execution policy
aws iam attach-role-policy `
  --role-name $ROLE_NAME `
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create custom policy
$customPolicy = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::media-ai-content/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "transcribe:StartTranscriptionJob",
        "transcribe:GetTranscriptionJob"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "rekognition:StartLabelDetection",
        "rekognition:GetLabelDetection",
        "rekognition:StartSegmentDetection",
        "rekognition:GetSegmentDetection"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:ap-south-1:586098609294:table/hivemind-*"
    }
  ]
}
"@

Set-Content -Path "lambda-policy.json" -Value $customPolicy

aws iam put-role-policy `
  --role-name $ROLE_NAME `
  --policy-name hivemind-lambda-policy `
  --policy-document file://lambda-policy.json

$ROLE_ARN = aws iam get-role `
  --role-name $ROLE_NAME `
  --query 'Role.Arn' `
  --output text

Write-Host "✅ Role created: $ROLE_ARN" -ForegroundColor Green
Set-Content -Path "role-arn.txt" -Value $ROLE_ARN

# Wait for role propagation
Write-Host "⏳ Waiting 10 seconds for IAM propagation..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Remove-Item trust-policy.json, lambda-policy.json
