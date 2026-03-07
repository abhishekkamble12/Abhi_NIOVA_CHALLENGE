"""Lambda handler for image analysis using Rekognition"""
import json
import os
import sys
sys.path.append('/opt/python')

from services.aws_ai_service import analyze_image, generate_text


def handler(event, context):
    """Analyze images for labels, text, and generate captions"""
    try:
        # Handle S3 event trigger
        if 'Records' in event:
            record = event['Records'][0]
            s3_bucket = record['s3']['bucket']['name']
            s3_key = record['s3']['object']['key']
        else:
            body = json.loads(event.get('body', '{}'))
            s3_bucket = body.get('bucket')
            s3_key = body.get('key')
        
        if not s3_bucket or not s3_key:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Bucket and key required'})
            }
        
        # Analyze image
        analysis = analyze_image(s3_bucket, s3_key)
        
        # Generate caption using Claude
        labels_text = ', '.join([l['name'] for l in analysis['labels'][:5]])
        caption_prompt = f"""Generate a short, engaging social media caption for an image containing: {labels_text}

Caption:"""
        
        caption = generate_text(caption_prompt, max_tokens=100, temperature=0.8)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'labels': analysis['labels'],
                'detected_text': analysis['text'],
                'generated_caption': caption.strip(),
                's3_uri': f's3://{s3_bucket}/{s3_key}'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
