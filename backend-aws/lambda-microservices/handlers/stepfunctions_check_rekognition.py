"""Lambda: Check Rekognition job status (no polling)"""
import json
import boto3
import os

rekognition = boto3.client('rekognition', region_name=os.getenv('AWS_REGION', 'ap-south-1'))


def handler(event, context):
    """Check Rekognition job status - single check, no polling"""
    try:
        job_id = event.get('jobId')
        job_type = event.get('jobType')  # 'scenes' or 'labels'
        
        if not all([job_id, job_type]):
            return {
                'statusCode': 400,
                'error': 'Missing required fields: jobId, jobType'
            }
        
        # Check job status based on type
        if job_type == 'scenes':
            response = rekognition.get_segment_detection(JobId=job_id)
            status = response['JobStatus']
            
            if status == 'SUCCEEDED':
                scenes = []
                for segment in response.get('Segments', []):
                    if segment['Type'] == 'SHOT':
                        scenes.append({
                            'startTime': segment['StartTimestampMillis'] / 1000,
                            'endTime': segment['EndTimestampMillis'] / 1000,
                            'confidence': segment['ShotSegment']['Confidence'],
                            'index': segment['ShotSegment']['Index']
                        })
                
                return {
                    'statusCode': 200,
                    'status': status,
                    'completed': True,
                    'scenes': scenes,
                    'sceneCount': len(scenes)
                }
            elif status == 'FAILED':
                return {
                    'statusCode': 500,
                    'status': status,
                    'completed': True,
                    'error': response.get('StatusMessage', 'Unknown error')
                }
            else:
                # IN_PROGRESS
                return {
                    'statusCode': 200,
                    'status': status,
                    'completed': False
                }
        
        elif job_type == 'labels':
            response = rekognition.get_label_detection(
                JobId=job_id,
                MaxResults=50,
                SortBy='TIMESTAMP'
            )
            status = response['JobStatus']
            
            if status == 'SUCCEEDED':
                # Aggregate labels
                label_map = {}
                for label_detection in response.get('Labels', []):
                    label = label_detection['Label']
                    label_name = label['Name']
                    
                    if label_name not in label_map:
                        label_map[label_name] = {
                            'name': label_name,
                            'confidence': label['Confidence'],
                            'timestamps': []
                        }
                    
                    label_map[label_name]['timestamps'].append(
                        label_detection['Timestamp'] / 1000
                    )
                
                labels = sorted(
                    label_map.values(),
                    key=lambda x: x['confidence'],
                    reverse=True
                )
                
                return {
                    'statusCode': 200,
                    'status': status,
                    'completed': True,
                    'labels': labels[:50],
                    'labelCount': len(labels)
                }
            elif status == 'FAILED':
                return {
                    'statusCode': 500,
                    'status': status,
                    'completed': True,
                    'error': response.get('StatusMessage', 'Unknown error')
                }
            else:
                # IN_PROGRESS
                return {
                    'statusCode': 200,
                    'status': status,
                    'completed': False
                }
        
        else:
            return {
                'statusCode': 400,
                'error': f'Invalid job type: {job_type}. Must be "scenes" or "labels"'
            }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'error': str(e),
            'completed': False
        }
