"""Lambda handler for news article analysis and semantic search"""
import json
import os
import sys
sys.path.append('/opt/python')

from services.aws_ai_service import generate_embeddings, generate_text


def handler(event, context):
    """Analyze news articles and generate embeddings"""
    try:
        body = json.loads(event.get('body', '{}'))
        
        action = body.get('action', 'analyze')
        
        if action == 'analyze':
            # Analyze single article
            article_text = body.get('text', '')
            title = body.get('title', '')
            
            if not article_text:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Article text required'})
                }
            
            # Generate embeddings
            embedding = generate_embeddings(article_text)
            
            # Generate summary
            summary_prompt = f"""Summarize this article in 2-3 sentences:

Title: {title}
Content: {article_text[:1000]}

Summary:"""
            
            summary = generate_text(summary_prompt, max_tokens=200, temperature=0.3)
            
            # Extract key topics
            topics_prompt = f"""Extract 3-5 key topics from this article as comma-separated tags:

{article_text[:500]}

Topics:"""
            
            topics = generate_text(topics_prompt, max_tokens=50, temperature=0.3)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'embedding_dim': len(embedding),
                    'summary': summary.strip(),
                    'topics': [t.strip() for t in topics.split(',')],
                    'title': title
                })
            }
        
        elif action == 'search':
            # Semantic search query
            query = body.get('query', '')
            
            if not query:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Query required'})
                }
            
            # Generate query embedding
            query_embedding = generate_embeddings(query)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'query': query,
                    'embedding_dim': len(query_embedding),
                    'message': 'Use this embedding for vector similarity search in Aurora pgvector'
                })
            }
        
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid action. Use "analyze" or "search"'})
            }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
