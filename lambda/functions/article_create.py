"""
Lambda: Create Article
Endpoint: POST /api/v1/articles
"""
import json
import sys
import os

# Add shared layer to path
sys.path.insert(0, '/opt/python')

from shared.response import success_response, error_response, parse_body
from shared.database import get_db_session

# Import models and services (from Lambda layer)
from app.models import Article
from app.services.vector_service import generate_embedding


async def create_article_handler(body: dict):
    """
    Business logic for creating article
    """
    # Validate required fields
    required_fields = ['title', 'content']
    for field in required_fields:
        if field not in body:
            raise ValueError(f"Missing required field: {field}")
    
    # Generate embedding
    text_for_embedding = f"{body['title']} {body['content']}"
    embedding = generate_embedding(text_for_embedding)
    
    # Create article
    async with get_db_session() as db:
        article = Article(
            title=body['title'],
            content=body['content'],
            summary=body.get('summary'),
            url=body.get('url'),
            source=body.get('source'),
            author=body.get('author'),
            category=body.get('category'),
            tags=body.get('tags', []),
            embedding=embedding
        )
        
        db.add(article)
        await db.flush()
        await db.refresh(article)
        
        return {
            'id': str(article.id),
            'title': article.title,
            'content': article.content,
            'summary': article.summary,
            'url': article.url,
            'source': article.source,
            'author': article.author,
            'category': article.category,
            'tags': article.tags,
            'created_at': article.created_at.isoformat(),
            'updated_at': article.updated_at.isoformat()
        }


def handler(event, context):
    """
    Lambda handler for POST /api/v1/articles
    
    API Gateway Event Structure:
    {
        "body": "{\"title\": \"...\", \"content\": \"...\"}",
        "headers": {...},
        "pathParameters": null,
        "queryStringParameters": null,
        "requestContext": {...}
    }
    """
    try:
        # Parse request body
        body = parse_body(event)
        
        # Import asyncio for running async code
        import asyncio
        
        # Run async handler
        result = asyncio.run(create_article_handler(body))
        
        # Return success response
        return success_response(result, status_code=201)
    
    except ValueError as e:
        return error_response(str(e), status_code=400, error_code='VALIDATION_ERROR')
    
    except Exception as e:
        print(f"Error creating article: {str(e)}")
        return error_response(
            'Internal server error',
            status_code=500,
            error_code='INTERNAL_ERROR'
        )
