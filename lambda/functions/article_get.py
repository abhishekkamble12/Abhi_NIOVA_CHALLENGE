"""
Lambda: Get Article
Endpoint: GET /api/v1/articles/{article_id}
"""
import sys
sys.path.insert(0, '/opt/python')

from shared.response import success_response, error_response, get_path_parameter
from shared.database import get_db_session
from sqlalchemy import select
from app.models import Article


async def get_article_handler(article_id: str):
    """
    Business logic for getting article
    """
    async with get_db_session() as db:
        result = await db.execute(
            select(Article).filter(Article.id == article_id)
        )
        article = result.scalar_one_or_none()
        
        if not article:
            raise ValueError(f"Article {article_id} not found")
        
        # Increment view count
        article.views += 1
        await db.flush()
        
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
            'views': article.views,
            'created_at': article.created_at.isoformat(),
            'updated_at': article.updated_at.isoformat()
        }


def handler(event, context):
    """
    Lambda handler for GET /api/v1/articles/{article_id}
    """
    try:
        # Get article ID from path
        article_id = get_path_parameter(event, 'article_id')
        
        if not article_id:
            return error_response('Missing article_id', status_code=400)
        
        # Run async handler
        import asyncio
        result = asyncio.run(get_article_handler(article_id))
        
        return success_response(result)
    
    except ValueError as e:
        return error_response(str(e), status_code=404, error_code='NOT_FOUND')
    
    except Exception as e:
        print(f"Error getting article: {str(e)}")
        return error_response('Internal server error', status_code=500)
