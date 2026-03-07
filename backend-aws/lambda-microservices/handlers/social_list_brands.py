"""Lambda: GET /api/v1/social/brands"""
import sys
import os
sys.path.insert(0, '/opt/python')
sys.path.insert(0, os.path.dirname(__file__))

from shared.lambda_utils import success_response, error_response
from services.database_service import list_brands

def handler(event, context):
    """List brands Lambda handler"""
    try:
        brands = list_brands()
        return success_response({"brands": brands})
    except Exception as e:
        return error_response(str(e), 500)
