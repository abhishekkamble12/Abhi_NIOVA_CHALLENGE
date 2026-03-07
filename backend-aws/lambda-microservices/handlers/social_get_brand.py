"""Lambda: GET /api/v1/social/brands/{brand_id}"""
import sys
import os
sys.path.insert(0, '/opt/python')
sys.path.insert(0, os.path.dirname(__file__))

from shared.lambda_utils import success_response, error_response
from services.database_service import get_brand

def handler(event, context):
    """Get brand Lambda handler"""
    try:
        brand_id = event['pathParameters']['brand_id']
        brand = get_brand(brand_id)
        
        if not brand:
            return error_response("Brand not found", 404)
        
        return success_response({"brand": brand})
    except Exception as e:
        return error_response(str(e), 500)
