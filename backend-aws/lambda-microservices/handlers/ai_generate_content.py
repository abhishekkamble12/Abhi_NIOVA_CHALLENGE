"""Lambda handler for AI-powered social media content generation"""
import json
import os
import sys
sys.path.append('/opt/python')

from services.aws_ai_service import generate_embeddings, generate_text


def handler(event, context):
    """Generate social media content using Bedrock Claude"""
    try:
        body = json.loads(event.get('body', '{}'))
        
        platform = body.get('platform', 'instagram')
        topic = body.get('topic', '')
        tone = body.get('tone', 'professional')
        
        if not topic:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Topic is required'})
            }
        
        # Generate content using Claude
        prompt = f"""Generate a {platform} post about: {topic}

Tone: {tone}
Requirements:
- Engaging hook in first line
- Platform-optimized format
- Include relevant emojis
- Add 3-5 hashtags

Generate only the post content, no explanations."""
        
        content = generate_text(prompt, max_tokens=500, temperature=0.8)
        
        # Generate embeddings for semantic search
        embedding = generate_embeddings(content)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'content': content,
                'platform': platform,
                'embedding_dim': len(embedding),
                'topic': topic
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
