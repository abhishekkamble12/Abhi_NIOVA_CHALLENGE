"""
Lambda: Semantic Article Search
Endpoint: GET /api/v1/articles/search/semantic
"""
import sys
sys.path.insert(0, '/opt/python')

from shared.response import success_response, error_response, get_query_parameter
from shared.database import get_db_session
from app.services.vector_service import search_similar_articles


async def search_articles_handler(query: str, limit: int = 10, min_similarity: float = 0.5):
    """
    Business logic for semantic article search
    """
    async with get_db_session() as db:
        results = await search_similar_articles(
            db=db,
            query_text=query,
            limit=limit,
            min_similarity=min_similarity
        )
        
        return [
            {
                'article': {
                    'id': str(article.id),
                    'title': article.title,
                    'summary': article.summary,
                    'url': article.url,
                    'source': article.source,
                    'category': article.category,
                    'tags': article.tags,
                    'created_at': article.created_at.isoformat()
                },
                'similarity': float(similarity)
            }
            for article, similarity in results
        ]


def handler(event, context):
    """
    Lambda handler for GET /api/v1/articles/search/semantic
    """
    try:
        # Parse query parameters
        query = get_query_parameter(event, 'query')
        
        if not query:
            return error_response('Missing query parameter', status_code=400)
        
        limit = int(get_query_parameter(event, 'limit', 10))
        min_similarity = float(get_query_parameter(event, 'min_similarity', 0.5))
        
        # Validate parameters
        if limit < 1 or limit > 100:
            return error_response('Limit must be between 1 and 100', status_code=400)
        
        if min_similarity < 0.0 or min_similarity > 1.0:
            return error_response('Min similarity must be between 0.0 and 1.0', status_code=400)
        
        # Run async handler
        import asyncio
        result = asyncio.run(search_articles_handler(query, limit, min_similarity))
        
        return success_response(result)
    
    except ValueError as e:
        return error_response(str(e), status_code=400)
    
    except Exception as e:
        print(f"Error searching articles: {str(e)}")
        return error_response('Internal server error', status_code=500)
