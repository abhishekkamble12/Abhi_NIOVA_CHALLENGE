"""AWS AI Services - Bedrock, Transcribe, Rekognition"""
import json
import os
import boto3
from typing import List, Dict, Any, Optional

# Initialize clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'ap-south-1'))
transcribe = boto3.client('transcribe', region_name=os.getenv('AWS_REGION', 'ap-south-1'))
rekognition = boto3.client('rekognition', region_name=os.getenv('AWS_REGION', 'ap-south-1'))
s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'ap-south-1'))


def generate_embeddings(text: str) -> List[float]:
    """Generate embeddings using Amazon Bedrock Titan"""
    response = bedrock_runtime.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({'inputText': text})
    )
    result = json.loads(response['body'].read())
    return result['embedding']


def generate_text(prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
    """Generate text using Amazon Bedrock Claude 3"""
    body = {
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': max_tokens,
        'temperature': temperature,
        'messages': [{'role': 'user', 'content': prompt}]
    }
    
    response = bedrock_runtime.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps(body)
    )
    
    result = json.loads(response['body'].read())
    return result['content'][0]['text']


def transcribe_audio(s3_uri: str, job_name: str, language_code: str = 'en-US') -> Dict[str, Any]:
    """Start transcription job using Amazon Transcribe"""
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': s3_uri},
        MediaFormat=s3_uri.split('.')[-1],
        LanguageCode=language_code,
        OutputBucketName=os.getenv('S3_BUCKET')
    )
    
    return {'job_name': job_name, 'status': 'IN_PROGRESS'}


def get_transcription_result(job_name: str) -> Optional[str]:
    """Get transcription result"""
    response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    job = response['TranscriptionJob']
    
    if job['TranscriptionJobStatus'] == 'COMPLETED':
        transcript_uri = job['Transcript']['TranscriptFileUri']
        # Download and parse transcript
        import urllib.request
        with urllib.request.urlopen(transcript_uri) as f:
            transcript_data = json.loads(f.read().decode())
        return transcript_data['results']['transcripts'][0]['transcript']
    
    return None


def detect_video_scenes(s3_bucket: str, s3_key: str) -> List[Dict[str, Any]]:
    """Detect scenes in video using Amazon Rekognition"""
    response = rekognition.start_segment_detection(
        Video={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}},
        SegmentTypes=['SHOT', 'TECHNICAL_CUE']
    )
    
    job_id = response['JobId']
    
    # Poll for completion
    while True:
        result = rekognition.get_segment_detection(JobId=job_id)
        status = result['JobStatus']
        
        if status == 'SUCCEEDED':
            segments = []
            for segment in result.get('Segments', []):
                if segment['Type'] == 'SHOT':
                    segments.append({
                        'start_time': segment['StartTimestampMillis'] / 1000,
                        'end_time': segment['EndTimestampMillis'] / 1000,
                        'confidence': segment['ShotSegment']['Confidence']
                    })
            return segments
        elif status == 'FAILED':
            raise Exception(f"Rekognition job failed: {result.get('StatusMessage')}")
        
        import time
        time.sleep(2)


def detect_labels_in_video(s3_bucket: str, s3_key: str, max_labels: int = 10) -> List[Dict[str, Any]]:
    """Detect labels/objects in video using Amazon Rekognition"""
    response = rekognition.start_label_detection(
        Video={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}},
        MinConfidence=70,
        Features=['GENERAL_LABELS']
    )
    
    job_id = response['JobId']
    
    # Poll for completion
    while True:
        result = rekognition.get_label_detection(JobId=job_id, MaxResults=max_labels)
        status = result['JobStatus']
        
        if status == 'SUCCEEDED':
            labels = []
            for label in result.get('Labels', []):
                labels.append({
                    'name': label['Label']['Name'],
                    'confidence': label['Label']['Confidence'],
                    'timestamp': label['Timestamp'] / 1000
                })
            return labels
        elif status == 'FAILED':
            raise Exception(f"Rekognition job failed: {result.get('StatusMessage')}")
        
        import time
        time.sleep(2)


def analyze_image(s3_bucket: str, s3_key: str) -> Dict[str, Any]:
    """Analyze image for labels and text using Amazon Rekognition"""
    # Detect labels
    labels_response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}},
        MaxLabels=10,
        MinConfidence=70
    )
    
    # Detect text
    text_response = rekognition.detect_text(
        Image={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}}
    )
    
    return {
        'labels': [{'name': l['Name'], 'confidence': l['Confidence']} for l in labels_response['Labels']],
        'text': [t['DetectedText'] for t in text_response['TextDetections'] if t['Type'] == 'LINE']
    }
