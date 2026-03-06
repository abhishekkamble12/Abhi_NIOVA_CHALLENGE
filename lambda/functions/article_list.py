"""
Lambda: List Articles
Endpoint: GET /api/v1/articles
"""
import sys
sys.path.insert(0, '/opt/python')

from shared.response import success_response, error_response, get_query_parameter
from shared.database import get_db_session
from sqlalchemy import select, func
from app.models import Article


async def list_articles_handler(category: str = None, page: int = 1, page_size: int = 20):
    """
    Business logic for listing articles
    """
    skip = (page - 1) * page_size
    
    async with get_db_session() as db:
        # Build query
        query = select(Article)
        count_query = select(func.count()).select_from(Article)
        
        if category:
            query = query.filter(Article.category == category)
            count_query = count_query.filter(Article.category == category)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get articles
        query = query.offset(skip).limit(page_size).order_by(Article.created_at.desc())
        result = await db.execute(query)
        articles = result.scalars().all()
        
        return {
            'articles': [
                {
                    'id': str(a.id),
                    'title': a.title,
                    'summary': a.summary,
                    'url': a.url,
                    'source': a.source,
                    'author': a.author,
                    'category': a.category,
                    'tags': a.tags,
                    'views': a.views,
                    'created_at': a.created_at.isoformat()
                }
                for a in articles
            ],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }


def handler(event, context):
    """
    Lambda handler for GET /api/v1/articles
    """
    try:
        # Parse query parameters
        category = get_query_parameter(event, 'category')
        page = int(get_query_parameter(event, 'page', 1))
        page_size = int(get_query_parameter(event, 'page_size', 20))
        
        # Validate pagination
        if page < 1:
            return error_response('Page must be >= 1', status_code=400)
        if page_size < 1 or page_size > 100:
            return error_response('Page size must be between 1 and 100', status_code=400)
        
        # Run async handler
        import asyncio
        result = asyncio.run(list_articles_handler(category, page, page_size))
        
        return success_response(result)
    
    except ValueError as e:
        return error_response(str(e), status_code=400)
    
    except Exception as e:
        print(f"Error listing articles: {str(e)}")
        return error_response('Internal server error', status_code=500)
