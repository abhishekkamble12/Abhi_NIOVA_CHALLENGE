"""Lambda: Check Amazon Transcribe job status"""
import json
import boto3
import os
import urllib.request

transcribe = boto3.client('transcribe', region_name=os.getenv('AWS_REGION', 'ap-south-1'))


def handler(event, context):
    """Check transcription job status and retrieve results"""
    try:
        # Parse input from Step Functions
        job_name = event.get('jobName')
        
        if not job_name:
            return {
                'statusCode': 400,
                'error': 'Missing required field: jobName'
            }
        
        # Get transcription job status
        response = transcribe.get_transcription_job(
            TranscriptionJobName=job_name
        )
        
        job = response['TranscriptionJob']
        status = job['TranscriptionJobStatus']
        
        # Return status
        result = {
            'statusCode': 200,
            'jobName': job_name,
            'status': status
        }
        
        # If completed, fetch transcript
        if status == 'COMPLETED':
            transcript_uri = job['Transcript']['TranscriptFileUri']
            
            # Download transcript
            with urllib.request.urlopen(transcript_uri) as f:
                transcript_data = json.loads(f.read().decode())
            
            # Extract transcript text
            transcript_text = transcript_data['results']['transcripts'][0]['transcript']
            
            result.update({
                'transcript': transcript_text,
                'transcriptUri': transcript_uri,
                'completed': True
            })
        elif status == 'FAILED':
            result.update({
                'error': job.get('FailureReason', 'Unknown error'),
                'completed': False
            })
        else:
            # IN_PROGRESS or QUEUED
            result['completed'] = False
        
        return result
        
    except transcribe.exceptions.BadRequestException:
        return {
            'statusCode': 404,
            'error': f'Transcription job not found: {job_name}'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'error': str(e)
        }
