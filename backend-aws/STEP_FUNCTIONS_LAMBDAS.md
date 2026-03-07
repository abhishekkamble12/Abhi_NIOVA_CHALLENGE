# Step Functions Lambda Implementations

## Overview

All missing Lambda functions referenced in `video-processing.json` Step Functions workflow have been implemented.

## Implemented Functions

### 1. hivemind-validate-video ✅

**File**: `stepfunctions_validate_video.py`

**Purpose**: Validate video file before processing

**Input**:
```json
{
  "videoId": "video-123",
  "s3Bucket": "hivemind-media",
  "s3Key": "videos/video.mp4"
}
```

**Output**:
```json
{
  "statusCode": 200,
  "valid": true,
  "videoId": "video-123",
  "s3Bucket": "hivemind-media",
  "s3Key": "videos/video.mp4",
  "fileSize": 10485760,
  "contentType": "video/mp4",
  "format": ".mp4"
}
```

**Validations**:
- File exists in S3
- File size < 5GB
- Format is supported (.mp4, .mov, .avi, .mkv, .webm)

---

### 2. hivemind-start-transcription ✅

**File**: `stepfunctions_start_transcription.py`

**Purpose**: Start Amazon Transcribe job

**Input**:
```json
{
  "videoId": "video-123",
  "s3Uri": "s3://hivemind-media/videos/video.mp4"
}
```

**Output**:
```json
{
  "statusCode": 200,
  "jobName": "transcribe-video-123-20240101-120000",
  "status": "IN_PROGRESS",
  "videoId": "video-123",
  "s3Uri": "s3://hivemind-media/videos/video.mp4",
  "mediaFormat": "mp4"
}
```

**Features**:
- Unique job name with timestamp
- Auto-detects media format
- Speaker labels enabled (up to 5 speakers)
- Outputs to S3 bucket

---

### 3. hivemind-check-transcription ✅

**File**: `stepfunctions_check_transcription.py`

**Purpose**: Check transcription job status and retrieve results

**Input**:
```json
{
  "jobName": "transcribe-video-123-20240101-120000"
}
```

**Output (In Progress)**:
```json
{
  "statusCode": 200,
  "jobName": "transcribe-video-123-20240101-120000",
  "status": "IN_PROGRESS",
  "completed": false
}
```

**Output (Completed)**:
```json
{
  "statusCode": 200,
  "jobName": "transcribe-video-123-20240101-120000",
  "status": "COMPLETED",
  "transcript": "Full transcript text...",
  "transcriptUri": "https://s3.amazonaws.com/...",
  "completed": true
}
```

**Features**:
- Polls Transcribe job status
- Downloads transcript when completed
- Returns full transcript text

---

### 4. hivemind-detect-scenes ✅

**File**: `stepfunctions_detect_scenes.py`

**Purpose**: Start Amazon Rekognition scene detection

**Input**:
```json
{
  "videoId": "video-123",
  "s3Bucket": "hivemind-media",
  "s3Key": "videos/video.mp4"
}
```

**Output**:
```json
{
  "statusCode": 200,
  "jobId": "rekognition-job-id",
  "videoId": "video-123",
  "s3Bucket": "hivemind-media",
  "s3Key": "videos/video.mp4",
  "status": "IN_PROGRESS"
}
```

**Helper Function**: `get_scene_results(job_id)`

**Output (Completed)**:
```json
{
  "statusCode": 200,
  "status": "COMPLETED",
  "scenes": [
    {
      "startTime": 0.0,
      "endTime": 5.2,
      "confidence": 98.5,
      "index": 0
    }
  ],
  "sceneCount": 15
}
```

**Features**:
- Detects SHOT and TECHNICAL_CUE segments
- Returns scene timestamps
- Confidence scores included

---

### 5. hivemind-detect-labels ✅

**File**: `stepfunctions_detect_labels.py`

**Purpose**: Start Amazon Rekognition label detection

**Input**:
```json
{
  "videoId": "video-123",
  "s3Bucket": "hivemind-media",
  "s3Key": "videos/video.mp4"
}
```

**Output**:
```json
{
  "statusCode": 200,
  "jobId": "rekognition-job-id",
  "videoId": "video-123",
  "s3Bucket": "hivemind-media",
  "s3Key": "videos/video.mp4",
  "status": "IN_PROGRESS"
}
```

**Helper Function**: `get_label_results(job_id, max_results=50)`

**Output (Completed)**:
```json
{
  "statusCode": 200,
  "status": "COMPLETED",
  "labels": [
    {
      "name": "Person",
      "confidence": 99.8,
      "instances": [],
      "timestamps": [0.0, 1.5, 3.2]
    }
  ],
  "labelCount": 25
}
```

**Features**:
- Detects objects, scenes, activities
- Minimum confidence: 70%
- Aggregates labels by name
- Includes bounding boxes for instances

---

### 6. hivemind-store-video-results ✅

**File**: `stepfunctions_store_video_results.py`

**Purpose**: Store all processing results in Aurora database

**Input**:
```json
{
  "videoId": "video-123",
  "results": [
    {"Payload": {"transcript": "...", "status": "COMPLETED"}},
    {"Payload": {"scenes": [...], "sceneCount": 15}},
    {"Payload": {"labels": [...], "labelCount": 25}}
  ],
  "detail": {
    "s3Bucket": "hivemind-media",
    "s3Key": "videos/video.mp4"
  }
}
```

**Output**:
```json
{
  "statusCode": 200,
  "videoId": "video-123",
  "stored": true,
  "summary": {
    "videoId": "video-123",
    "s3Url": "s3://hivemind-media/videos/video.mp4",
    "duration": 120.5,
    "transcription": {
      "status": "completed",
      "length": 1500
    },
    "scenes": {
      "count": 15,
      "status": "completed"
    },
    "labels": {
      "count": 25,
      "status": "completed",
      "topLabels": ["Person", "Car", "Building", "Sky", "Tree"]
    }
  }
}
```

**Features**:
- Stores video metadata in Aurora
- Aggregates results from parallel branches
- Calculates video duration from scenes
- Returns processing summary

---

## Step Functions Integration

### Video Processing Workflow

```
VideoUploaded Event
  ↓
ValidateVideo
  ↓
ParallelProcessing
  ├─ StartTranscription → WaitForTranscription → CheckTranscription
  ├─ DetectScenes
  └─ DetectLabels
  ↓
StoreResults
  ↓
PublishVideoProcessed Event
```

### Updated Step Functions Definition

The existing `video-processing.json` references these functions correctly:

```json
{
  "ValidateVideo": {
    "Type": "Task",
    "Resource": "arn:aws:states:::lambda:invoke",
    "Parameters": {
      "FunctionName": "hivemind-validate-video",
      "Payload": {
        "videoId.$": "$.detail.videoId",
        "s3Bucket.$": "$.detail.s3Bucket",
        "s3Key.$": "$.detail.s3Key"
      }
    }
  }
}
```

---

## CloudFormation Template

Add these functions to `template-api-gateway.yaml`:

```yaml
ValidateVideoFunction:
  Type: AWS::Serverless::Function
  Properties:
    FunctionName: hivemind-validate-video
    CodeUri: lambda-microservices/
    Handler: handlers.stepfunctions_validate_video.handler
    Policies:
      - S3ReadPolicy:
          BucketName: !Ref MediaBucket

StartTranscriptionFunction:
  Type: AWS::Serverless::Function
  Properties:
    FunctionName: hivemind-start-transcription
    CodeUri: lambda-microservices/
    Handler: handlers.stepfunctions_start_transcription.handler
    Timeout: 60
    Policies:
      - Statement:
          - Effect: Allow
            Action:
              - transcribe:StartTranscriptionJob
            Resource: '*'

CheckTranscriptionFunction:
  Type: AWS::Serverless::Function
  Properties:
    FunctionName: hivemind-check-transcription
    CodeUri: lambda-microservices/
    Handler: handlers.stepfunctions_check_transcription.handler
    Policies:
      - Statement:
          - Effect: Allow
            Action:
              - transcribe:GetTranscriptionJob
            Resource: '*'

DetectScenesFunction:
  Type: AWS::Serverless::Function
  Properties:
    FunctionName: hivemind-detect-scenes
    CodeUri: lambda-microservices/
    Handler: handlers.stepfunctions_detect_scenes.handler
    Timeout: 60
    Policies:
      - Statement:
          - Effect: Allow
            Action:
              - rekognition:StartSegmentDetection
              - rekognition:GetSegmentDetection
            Resource: '*'

DetectLabelsFunction:
  Type: AWS::Serverless::Function
  Properties:
    FunctionName: hivemind-detect-labels
    CodeUri: lambda-microservices/
    Handler: handlers.stepfunctions_detect_labels.handler
    Timeout: 60
    Policies:
      - Statement:
          - Effect: Allow
            Action:
              - rekognition:StartLabelDetection
              - rekognition:GetLabelDetection
            Resource: '*'

StoreVideoResultsFunction:
  Type: AWS::Serverless::Function
  Properties:
    FunctionName: hivemind-store-video-results
    CodeUri: lambda-microservices/
    Handler: handlers.stepfunctions_store_video_results.handler
    Layers:
      - !Ref SharedLayer
    Environment:
      Variables:
        DB_HOST: !Ref DBHost
        DB_NAME: hiveminddb
        DB_USER: hivemind
        DB_PASSWORD: !Ref DBPassword
```

---

## Testing

### Test Individual Functions

```bash
# Validate Video
aws lambda invoke \
  --function-name hivemind-validate-video \
  --payload '{"videoId":"test-123","s3Bucket":"my-bucket","s3Key":"videos/test.mp4"}' \
  response.json

# Start Transcription
aws lambda invoke \
  --function-name hivemind-start-transcription \
  --payload '{"videoId":"test-123","s3Uri":"s3://my-bucket/videos/test.mp4"}' \
  response.json

# Check Transcription
aws lambda invoke \
  --function-name hivemind-check-transcription \
  --payload '{"jobName":"transcribe-test-123-20240101-120000"}' \
  response.json
```

### Test Step Functions Workflow

```bash
# Start execution
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:ap-south-1:123456789012:stateMachine:hivemind-video-processing \
  --input '{"detail":{"videoId":"test-123","s3Bucket":"my-bucket","s3Key":"videos/test.mp4"}}'

# Check execution status
aws stepfunctions describe-execution \
  --execution-arn <execution-arn>
```

---

## Error Handling

All functions return structured error responses:

```json
{
  "statusCode": 500,
  "error": "Error message",
  "valid": false  // for validate-video
}
```

Step Functions can catch errors using:

```json
{
  "Catch": [{
    "ErrorEquals": ["States.ALL"],
    "Next": "ProcessingFailed"
  }]
}
```

---

## Summary

### Implemented Functions
1. ✅ `hivemind-validate-video` - S3 file validation
2. ✅ `hivemind-start-transcription` - Start Transcribe job
3. ✅ `hivemind-check-transcription` - Poll Transcribe status
4. ✅ `hivemind-detect-scenes` - Start Rekognition scene detection
5. ✅ `hivemind-detect-labels` - Start Rekognition label detection
6. ✅ `hivemind-store-video-results` - Store results in Aurora

### Key Features
- ✅ Step Functions compatible input/output
- ✅ Structured error responses
- ✅ AWS SDK integration (Transcribe, Rekognition, S3)
- ✅ Non-blocking async job patterns
- ✅ Database integration for results storage

All functions are ready for deployment and Step Functions integration.
