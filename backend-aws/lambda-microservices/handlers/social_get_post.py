"""Lambda: GET /api/v1/social/posts/{post_id}"""
import asyncio
import sys
import os
sys.path.insert(0, '/opt/python')
sys.path.insert(0, os.path.dirname(__file__))

from shared.lambda_utils import success_response, error_response, get_path_param
from services.social_service import get_post_logic

def handler(event, context):
    """Get post Lambda handler"""
    try:
        post_id = get_path_param(event, 'post_id')
        if not post_id:
            return error_response("Missing post_id", 400)
        
        result = asyncio.run(get_post_logic(int(post_id)))
        if not result:
            return error_response("Post not found", 404)
        
        return success_response(result)
        
    except Exception as e:
        return error_response(str(e), 500)
