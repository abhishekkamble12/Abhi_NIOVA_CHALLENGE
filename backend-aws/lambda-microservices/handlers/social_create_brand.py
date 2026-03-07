"""Lambda: POST /api/v1/social/brands"""
import sys
import os
import json
import uuid
sys.path.insert(0, '/opt/python')
sys.path.insert(0, os.path.dirname(__file__))

from shared.lambda_utils import success_response, error_response
from services.database_service import create_brand

def handler(event, context):
    """Create brand Lambda handler"""
    try:
        body = json.loads(event['body'])
        name = body['name']
        industry = body.get('industry', '')
        
        brand_id = str(uuid.uuid4())
        brand = create_brand(brand_id, name, industry)
        
        return success_response({"brand": brand}, 201)
    except Exception as e:
        return error_response(str(e), 500)
