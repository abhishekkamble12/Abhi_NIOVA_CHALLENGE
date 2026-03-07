"""Lambda: Store video processing results in database"""
import json
import os
import sys
sys.path.append('/opt/python')

from services.database_service import store_video_metadata, update_video_transcription


def handler(event, context):
    """Store video processing results in Aurora"""
    try:
        # Parse input from Step Functions
        video_id = event.get('videoId')
        results = event.get('results', [])
        
        if not video_id:
            return {
                'statusCode': 400,
                'error': 'Missing required field: videoId'
            }
        
        # Extract results from parallel processing branches
        transcription_result = None
        scenes_result = None
        labels_result = None
        
        for result in results:
            if 'Payload' in result:
                payload = result['Payload']
                
                # Transcription result
                if 'transcript' in payload:
                    transcription_result = payload
                
                # Scenes result
                elif 'scenes' in payload:
                    scenes_result = payload
                
                # Labels result
                elif 'labels' in payload:
                    labels_result = payload
        
        # Get S3 URL and duration from original event
        s3_bucket = event.get('detail', {}).get('s3Bucket')
        s3_key = event.get('detail', {}).get('s3Key')
        s3_url = f's3://{s3_bucket}/{s3_key}' if s3_bucket and s3_key else None
        
        # Calculate duration from scenes
        duration = 0
        if scenes_result and scenes_result.get('scenes'):
            last_scene = scenes_result['scenes'][-1]
            duration = last_scene.get('endTime', 0)
        
        # Store video metadata
        video_data = store_video_metadata(
            video_id=video_id,
            s3_url=s3_url or f's3://unknown/{video_id}',
            duration=duration,
            transcription=transcription_result.get('transcript') if transcription_result else None
        )
        
        # Prepare summary
        summary = {
            'videoId': video_id,
            's3Url': s3_url,
            'duration': duration,
            'transcription': {
                'status': 'completed' if transcription_result else 'failed',
                'length': len(transcription_result.get('transcript', '')) if transcription_result else 0
            },
            'scenes': {
                'count': scenes_result.get('sceneCount', 0) if scenes_result else 0,
                'status': 'completed' if scenes_result else 'failed'
            },
            'labels': {
                'count': labels_result.get('labelCount', 0) if labels_result else 0,
                'status': 'completed' if labels_result else 'failed',
                'topLabels': [l['name'] for l in labels_result.get('labels', [])[:5]] if labels_result else []
            }
        }
        
        return {
            'statusCode': 200,
            'videoId': video_id,
            'stored': True,
            'summary': summary
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'error': str(e),
            'stored': False
        }
