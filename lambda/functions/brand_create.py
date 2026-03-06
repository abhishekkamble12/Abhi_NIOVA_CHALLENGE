"""
Lambda: Create Brand
Endpoint: POST /api/v1/brands
"""
import sys
sys.path.insert(0, '/opt/python')

from shared.response import success_response, error_response, parse_body, get_user_id
from shared.database import get_db_session
from app.models import Brand
from app.services.vector_service import generate_embedding


async def create_brand_handler(user_id: str, body: dict):
    """
    Business logic for creating brand
    """
    # Validate required fields
    if 'name' not in body:
        raise ValueError("Missing required field: name")
    
    # Generate embedding
    text_for_embedding = f"{body['name']} {body.get('description', '')} {body.get('brand_voice', '')}"
    embedding = generate_embedding(text_for_embedding)
    
    # Create brand
    async with get_db_session() as db:
        brand = Brand(
            user_id=user_id,
            name=body['name'],
            description=body.get('description'),
            industry=body.get('industry'),
            tone=body.get('tone'),
            target_audience=body.get('target_audience'),
            brand_voice=body.get('brand_voice'),
            embedding=embedding
        )
        
        db.add(brand)
        await db.flush()
        await db.refresh(brand)
        
        return {
            'id': str(brand.id),
            'user_id': str(brand.user_id),
            'name': brand.name,
            'description': brand.description,
            'industry': brand.industry,
            'tone': brand.tone,
            'target_audience': brand.target_audience,
            'brand_voice': brand.brand_voice,
            'created_at': brand.created_at.isoformat(),
            'updated_at': brand.updated_at.isoformat()
        }


def handler(event, context):
    """
    Lambda handler for POST /api/v1/brands
    """
    try:
        # Get user ID from authorizer
        user_id = get_user_id(event)
        
        if not user_id:
            return error_response('Unauthorized', status_code=401)
        
        # Parse request body
        body = parse_body(event)
        
        # Run async handler
        import asyncio
        result = asyncio.run(create_brand_handler(user_id, body))
        
        return success_response(result, status_code=201)
    
    except ValueError as e:
        return error_response(str(e), status_code=400, error_code='VALIDATION_ERROR')
    
    except Exception as e:
        print(f"Error creating brand: {str(e)}")
        return error_response('Internal server error', status_code=500)
