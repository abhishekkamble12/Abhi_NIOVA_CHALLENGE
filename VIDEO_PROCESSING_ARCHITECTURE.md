# 🎬 Video Processing Architecture for HiveMind

## Executive Summary

This document details the **video intelligence pipeline** for HiveMind using AWS services. The architecture processes video uploads, detects scenes, generates captions, creates embeddings, and enables semantic search across video content.

**Core Services:**
- Amazon S3 (storage)
- AWS Lambda (processing triggers)
- AWS Step Functions (orchestration)
- Amazon Rekognition (scene detection)
- Amazon Transcribe (speech-to-text)
- Amazon Bedrock (caption generation + embeddings)
- OpenSearch (vector search)

---

## 📊 1. Video Processing Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER UPLOAD                               │
│  Frontend → API Gateway → Lambda (presigned URL)            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    S3 UPLOAD                                 │
│  video-uploads-bucket/{user_id}/{video_id}/original.mp4    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼ (S3 Event)
┌─────────────────────────────────────────────────────────────┐
│                 STEP FUNCTIONS WORKFLOW                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Validate Video                                    │  │
│  │  2. Extract Metadata                                  │  │
│  │  3. Parallel Processing:                              │  │
│  │     ├─ Rekognition (Scene Detection)                 │  │
│  │     ├─ Transcribe (Speech-to-Text)                   │  │
│  │     └─ Thumbnail Generation                           │  │
│  │  4. Process Results                                   │  │
│  │  5. Generate Captions (Bedrock)                       │  │
│  │  6. Generate Embeddings (Bedrock)                     │  │
│  │  7. Store Metadata (Aurora + DynamoDB)                │  │
│  │  8. Index Vectors (OpenSearch)                        │  │
│  │  9. Notify User (SNS)                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  PROCESSED OUTPUT                            │
│  - Video metadata in Aurora                                 │
│  - Scenes in DynamoDB                                       │
│  - Captions in Aurora                                       │
│  - Embeddings in OpenSearch                                 │
│  - Processed video in S3                                    │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 S3 Bucket Structure

```
video-uploads-bucket/
├── {user_id}/
│   └── {video_id}/
│       ├── original.mp4
│       ├── metadata.json
│       └── thumbnail.jpg

video-processed-bucket/
├── {user_id}/
│   └── {video_id}/
│       ├── optimized/
│       │   ├── instagram.mp4
│       │   ├── youtube.mp4
│       │   └── tiktok.mp4
│       ├── thumbnails/
│       │   ├── frame_001.jpg
│       │   ├── frame_002.jpg
│       │   └── selected.jpg
│       └── captions/
│           ├── captions.srt
│           └── captions.vtt

video-transcripts-bucket/
└── {video_id}/
    ├── transcript.json
    └── transcript.txt
```

---

## 🔄 2. Video Upload Workflow

### 2.1 Upload Flow

```python
# Lambda: video-upload-handler

import boto3
import json
from datetime import datetime, timedelta
import uuid

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Generate presigned URL for video upload
    """
    
    # Parse request
    body = json.loads(event['body'])
    user_id = event['requestContext']['authorizer']['claims']['sub']
    
    video_id = str(uuid.uuid4())
    filename = body.get('filename', 'video.mp4')
    content_type = body.get('content_type', 'video/mp4')
    file_size = body.get('file_size', 0)
    
    # Validate file size (max 2GB)
    if file_size > 2 * 1024 * 1024 * 1024:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'File too large. Max 2GB.'})
        }
    
    # Generate S3 key
    s3_key = f"{user_id}/{video_id}/original.mp4"
    
    # Generate presigned URL (valid for 1 hour)
    presigned_url = s3.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': 'video-uploads-bucket',
            'Key': s3_key,
            'ContentType': content_type
        },
        ExpiresIn=3600
    )
    
    # Create video record in DynamoDB
    videos_table = dynamodb.Table('videos-table')
    videos_table.put_item(
        Item={
            'id': video_id,
            'user_id': user_id,
            'filename': filename,
            'file_size': file_size,
            's3_key': s3_key,
            'status': 'uploading',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'video_id': video_id,
            'upload_url': presigned_url,
            'expires_in': 3600
        })
    }
```

### 2.2 Upload Completion Trigger

```python
# Lambda: video-upload-complete

import boto3
import json

stepfunctions = boto3.client('stepfunctions')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Triggered by S3 upload completion
    """
    
    # Parse S3 event
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        size = record['s3']['object']['size']
        
        # Extract video_id from key: {user_id}/{video_id}/original.mp4
        parts = key.split('/')
        user_id = parts[0]
        video_id = parts[1]
        
        # Update video status
        videos_table = dynamodb.Table('videos-table')
        videos_table.update_item(
            Key={'id': video_id},
            UpdateExpression='SET #status = :status, file_size = :size',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'processing',
                ':size': size
            }
        )
        
        # Start Step Functions workflow
        stepfunctions.start_execution(
            stateMachineArn='arn:aws:states:us-east-1:account:stateMachine:video-processing',
            name=f"video-{video_id}-{int(datetime.utcnow().timestamp())}",
            input=json.dumps({
                'video_id': video_id,
                'user_id': user_id,
                'bucket': bucket,
                'key': key,
                'size': size
            })
        )
    
    return {'statusCode': 200}
```

---

## 🎯 3. Scene Detection Pipeline

### 3.1 Rekognition Integration

```python
# Lambda: video-scene-detection

import boto3
import json

rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Start Rekognition scene detection
    """
    
    video_id = event['video_id']
    bucket = event['bucket']
    key = event['key']
    
    # Start segment detection
    response = rekognition.start_segment_detection(
        Video={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        },
        SegmentTypes=['SHOT', 'TECHNICAL_CUE'],
        Filters={
            'TechnicalCueFilter': {
                'MinSegmentConfidence': 70,
                'BlackFrame': {
                    'MaxPixelThreshold': 0.2,
                    'MinCoveragePercentage': 99
                }
            },
            'ShotFilter': {
                'MinSegmentConfidence': 70
            }
        },
        NotificationChannel={
            'SNSTopicArn': 'arn:aws:sns:us-east-1:account:rekognition-results',
            'RoleArn': 'arn:aws:iam::account:role/RekognitionSNSRole'
        }
    )
    
    job_id = response['JobId']
    
    # Store job ID
    videos_table = dynamodb.Table('videos-table')
    videos_table.update_item(
        Key={'id': video_id},
        UpdateExpression='SET rekognition_job_id = :job_id',
        ExpressionAttributeValues={':job_id': job_id}
    )
    
    return {
        'video_id': video_id,
        'rekognition_job_id': job_id,
        'status': 'started'
    }


def get_scene_results(job_id):
    """
    Retrieve Rekognition results
    """
    
    response = rekognition.get_segment_detection(JobId=job_id)
    
    scenes = []
    
    # Process shots
    for segment in response.get('Segments', []):
        if segment['Type'] == 'SHOT':
            shot = segment['ShotSegment']
            scenes.append({
                'type': 'shot',
                'start_time': segment['StartTimestampMillis'] / 1000,
                'end_time': segment['EndTimestampMillis'] / 1000,
                'duration': segment['DurationMillis'] / 1000,
                'confidence': shot['Confidence'],
                'index': shot['Index']
            })
        
        elif segment['Type'] == 'TECHNICAL_CUE':
            cue = segment['TechnicalCueSegment']
            scenes.append({
                'type': cue['Type'].lower(),
                'start_time': segment['StartTimestampMillis'] / 1000,
                'end_time': segment['EndTimestampMillis'] / 1000,
                'duration': segment['DurationMillis'] / 1000,
                'confidence': cue['Confidence']
            })
    
    return scenes
```

### 3.2 Scene Storage

```python
# Lambda: video-store-scenes

import boto3
import json
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Store detected scenes
    """
    
    video_id = event['video_id']
    scenes = event['scenes']
    
    scenes_table = dynamodb.Table('video-scenes-table')
    
    # Store each scene
    for i, scene in enumerate(scenes):
        scene_id = f"{video_id}_{i}"
        
        scenes_table.put_item(
            Item={
                'id': scene_id,
                'video_id': video_id,
                'scene_index': i,
                'scene_type': scene['type'],
                'start_time': Decimal(str(scene['start_time'])),
                'end_time': Decimal(str(scene['end_time'])),
                'duration': Decimal(str(scene['duration'])),
                'confidence': Decimal(str(scene['confidence'])),
                'created_at': datetime.utcnow().isoformat()
            }
        )
    
    return {
        'video_id': video_id,
        'scenes_stored': len(scenes)
    }
```

---

## 💬 4. Caption Generation with Bedrock

### 4.1 Transcription Pipeline

```python
# Lambda: video-transcribe

import boto3
import json

transcribe = boto3.client('transcribe')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Start transcription job
    """
    
    video_id = event['video_id']
    bucket = event['bucket']
    key = event['key']
    
    job_name = f"transcribe-{video_id}"
    
    # Start transcription
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={
            'MediaFileUri': f"s3://{bucket}/{key}"
        },
        MediaFormat='mp4',
        LanguageCode='en-US',
        Settings={
            'ShowSpeakerLabels': True,
            'MaxSpeakerLabels': 5,
            'ChannelIdentification': False
        },
        Subtitles={
            'Formats': ['srt', 'vtt'],
            'OutputStartIndex': 1
        },
        OutputBucketName='video-transcripts-bucket',
        OutputKey=f"{video_id}/"
    )
    
    return {
        'video_id': video_id,
        'transcription_job_name': job_name,
        'status': 'started'
    }


def get_transcript(job_name):
    """
    Retrieve transcription results
    """
    
    response = transcribe.get_transcription_job(
        TranscriptionJobName=job_name
    )
    
    job = response['TranscriptionJob']
    
    if job['TranscriptionJobStatus'] != 'COMPLETED':
        return None
    
    # Download transcript
    transcript_uri = job['Transcript']['TranscriptFileUri']
    
    import requests
    transcript_data = requests.get(transcript_uri).json()
    
    return {
        'full_transcript': transcript_data['results']['transcripts'][0]['transcript'],
        'items': transcript_data['results']['items'],
        'subtitles': {
            'srt': job['Subtitles']['SubtitleFileUris'][0],
            'vtt': job['Subtitles']['SubtitleFileUris'][1]
        }
    }
```

### 4.2 AI Caption Generation

```python
# Lambda: video-generate-captions

import boto3
import json

bedrock = boto3.client('bedrock-runtime')

async def lambda_handler(event, context):
    """
    Generate captions for video scenes using Bedrock
    """
    
    video_id = event['video_id']
    scenes = event['scenes']
    transcript = event['transcript']
    
    captions = []
    
    for scene in scenes:
        # Extract transcript segment for this scene
        transcript_segment = extract_transcript_segment(
            transcript,
            scene['start_time'],
            scene['end_time']
        )
        
        # Generate caption with Bedrock
        caption = await generate_caption(
            scene=scene,
            transcript_segment=transcript_segment
        )
        
        captions.append(caption)
    
    return {
        'video_id': video_id,
        'captions': captions
    }


def extract_transcript_segment(transcript, start_time, end_time):
    """
    Extract transcript for time range
    """
    
    segment_words = []
    
    for item in transcript['items']:
        if item['type'] != 'pronunciation':
            continue
        
        item_start = float(item['start_time'])
        item_end = float(item['end_time'])
        
        # Check if word is in time range
        if item_start >= start_time and item_end <= end_time:
            segment_words.append(item['alternatives'][0]['content'])
    
    return ' '.join(segment_words)


async def generate_caption(scene, transcript_segment):
    """
    Generate engaging caption using Bedrock
    """
    
    prompt = f"""Generate a concise, engaging caption for this video scene.

Scene Details:
- Time: {scene['start_time']:.1f}s - {scene['end_time']:.1f}s
- Duration: {scene['duration']:.1f}s
- Type: {scene['type']}

Spoken Content:
{transcript_segment if transcript_segment else '[No speech detected]'}

Requirements:
- Max 100 characters
- Engaging and clear
- Include relevant emoji
- Match the scene tone

Output JSON:
{{
  "caption": "...",
  "emoji": "..."
}}"""
    
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 200,
            'temperature': 0.7,
            'messages': [{
                'role': 'user',
                'content': prompt
            }]
        })
    )
    
    result = json.loads(response['body'].read())
    caption_data = json.loads(result['content'][0]['text'])
    
    return {
        'scene_id': scene.get('id'),
        'start_time': scene['start_time'],
        'end_time': scene['end_time'],
        'caption': caption_data['caption'],
        'emoji': caption_data.get('emoji', ''),
        'transcript': transcript_segment
    }
```

---

## 🔢 5. Embedding Generation

### 5.1 Scene Embedding Pipeline

```python
# Lambda: video-generate-embeddings

import boto3
import json

bedrock = boto3.client('bedrock-runtime')
opensearch = get_opensearch_client()

async def lambda_handler(event, context):
    """
    Generate embeddings for video scenes
    """
    
    video_id = event['video_id']
    scenes = event['scenes']
    captions = event['captions']
    
    embeddings = []
    
    # Generate embeddings for each scene
    for scene, caption in zip(scenes, captions):
        # Combine scene info + caption for embedding
        scene_text = f"{caption['caption']} {caption.get('transcript', '')}"
        
        # Generate embedding with Bedrock
        embedding = await generate_embedding(scene_text)
        
        embeddings.append({
            'scene_id': scene.get('id'),
            'embedding': embedding,
            'text': scene_text
        })
    
    return {
        'video_id': video_id,
        'embeddings': embeddings
    }


async def generate_embedding(text):
    """
    Generate embedding using Bedrock Titan
    """
    
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({
            'inputText': text
        })
    )
    
    result = json.loads(response['body'].read())
    return result['embedding']
```

### 5.2 OpenSearch Indexing

```python
# Lambda: video-index-opensearch

import boto3
from opensearchpy import OpenSearch

opensearch = get_opensearch_client()

async def lambda_handler(event, context):
    """
    Index video scenes in OpenSearch
    """
    
    video_id = event['video_id']
    scenes = event['scenes']
    captions = event['captions']
    embeddings = event['embeddings']
    
    # Prepare bulk index operations
    bulk_data = []
    
    for scene, caption, emb in zip(scenes, captions, embeddings):
        scene_id = scene.get('id')
        
        # Index action
        bulk_data.append({
            'index': {
                '_index': 'video-scenes-index',
                '_id': scene_id
            }
        })
        
        # Document
        bulk_data.append({
            'id': scene_id,
            'video_id': video_id,
            'scene_type': scene['type'],
            'start_time': scene['start_time'],
            'end_time': scene['end_time'],
            'duration': scene['duration'],
            'caption': caption['caption'],
            'transcript': caption.get('transcript', ''),
            'embedding': emb['embedding'],
            'indexed_at': datetime.utcnow().isoformat()
        })
    
    # Bulk index
    response = opensearch.bulk(body=bulk_data)
    
    return {
        'video_id': video_id,
        'scenes_indexed': len(scenes),
        'errors': response.get('errors', False)
    }
```

---

## 🔄 6. Complete Step Functions Workflow

```json
{
  "Comment": "Video Processing Workflow",
  "StartAt": "ValidateVideo",
  "States": {
    "ValidateVideo": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:video-validate",
      "Next": "ExtractMetadata",
      "Catch": [{
        "ErrorEquals": ["States.ALL"],
        "Next": "ProcessingFailed"
      }]
    },
    
    "ExtractMetadata": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:video-extract-metadata",
      "Next": "ParallelProcessing"
    },
    
    "ParallelProcessing": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "StartRekognition",
          "States": {
            "StartRekognition": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:video-scene-detection",
              "Next": "WaitForRekognition"
            },
            "WaitForRekognition": {
              "Type": "Wait",
              "Seconds": 30,
              "Next": "CheckRekognition"
            },
            "CheckRekognition": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:video-check-rekognition",
              "Next": "RekognitionComplete",
              "Retry": [{
                "ErrorEquals": ["JobNotComplete"],
                "BackoffRate": 1.5,
                "IntervalSeconds": 30,
                "MaxAttempts": 20
              }]
            },
            "RekognitionComplete": {
              "Type": "Pass",
              "End": true
            }
          }
        },
        {
          "StartAt": "StartTranscribe",
          "States": {
            "StartTranscribe": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:video-transcribe",
              "Next": "WaitForTranscribe"
            },
            "WaitForTranscribe": {
              "Type": "Wait",
              "Seconds": 30,
              "Next": "CheckTranscribe"
            },
            "CheckTranscribe": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:video-check-transcribe",
              "Next": "TranscribeComplete",
              "Retry": [{
                "ErrorEquals": ["JobNotComplete"],
                "BackoffRate": 1.5,
                "IntervalSeconds": 30,
                "MaxAttempts": 20
              }]
            },
            "TranscribeComplete": {
              "Type": "Pass",
              "End": true
            }
          }
        },
        {
          "StartAt": "GenerateThumbnail",
          "States": {
            "GenerateThumbnail": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:video-thumbnail",
              "End": true
            }
          }
        }
      ],
      "Next": "ProcessResults"
    },
    
    "ProcessResults": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:video-process-results",
      "Next": "GenerateCaptions"
    },
    
    "GenerateCaptions": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:video-generate-captions",
      "Next": "GenerateEmbeddings"
    },
    
    "GenerateEmbeddings": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:video-generate-embeddings",
      "Next": "StoreData"
    },
    
    "StoreData": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "StoreScenes",
          "States": {
            "StoreScenes": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:video-store-scenes",
              "End": true
            }
          }
        },
        {
          "StartAt": "IndexOpenSearch",
          "States": {
            "IndexOpenSearch": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:video-index-opensearch",
              "End": true
            }
          }
        }
      ],
      "Next": "NotifyUser"
    },
    
    "NotifyUser": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:user-notifications",
        "Message.$": "$.notification_message"
      },
      "Next": "ProcessingComplete"
    },
    
    "ProcessingComplete": {
      "Type": "Succeed"
    },
    
    "ProcessingFailed": {
      "Type": "Fail",
      "Error": "VideoProcessingError",
      "Cause": "Video processing failed"
    }
  }
}
```

---

## 📊 7. Performance Metrics

```yaml
Processing Times:
  - Upload: < 5 min (depends on file size)
  - Scene Detection: 1-3 min per video minute
  - Transcription: 0.5-1 min per video minute
  - Caption Generation: 2-5 sec per scene
  - Embedding Generation: 100ms per scene
  - Total: 5-15 min for 5-min video

Costs (per video):
  - S3 Storage: $0.023 per GB/month
  - Rekognition: $0.10 per min
  - Transcribe: $0.024 per min
  - Bedrock Embeddings: $0.0001 per 1K tokens
  - Bedrock Captions: $0.00025 per 1K tokens
  - Total: ~$0.50-2.00 per 5-min video

Scalability:
  - Concurrent videos: 100+
  - Max video size: 2GB
  - Max duration: 2 hours
  - Supported formats: MP4, MOV, AVI
```

---

*Document Version: 1.0*  
*Architecture: AWS-Native Video Processing*  
*Services: S3, Lambda, Step Functions, Rekognition, Transcribe, Bedrock*
