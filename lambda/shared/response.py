"""
Lambda response utilities for API Gateway integration
"""
import json
from typing import Any, Dict, Optional


def success_response(
    body: Any,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> Dict:
    """
    Format successful API Gateway response
    """
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body, default=str)
    }


def error_response(
    message: str,
    status_code: int = 400,
    error_code: Optional[str] = None
) -> Dict:
    """
    Format error API Gateway response
    """
    body = {
        'error': message,
        'statusCode': status_code
    }
    
    if error_code:
        body['errorCode'] = error_code
    
    return success_response(body, status_code)


def parse_body(event: Dict) -> Dict:
    """
    Parse request body from API Gateway event
    """
    body = event.get('body', '{}')
    
    if isinstance(body, str):
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}
    
    return body


def get_path_parameter(event: Dict, param: str) -> Optional[str]:
    """
    Get path parameter from API Gateway event
    """
    path_params = event.get('pathParameters') or {}
    return path_params.get(param)


def get_query_parameter(event: Dict, param: str, default: Any = None) -> Any:
    """
    Get query parameter from API Gateway event
    """
    query_params = event.get('queryStringParameters') or {}
    return query_params.get(param, default)


def get_user_id(event: Dict) -> Optional[str]:
    """
    Extract user ID from authorizer context
    """
    request_context = event.get('requestContext', {})
    authorizer = request_context.get('authorizer', {})
    
    # From Cognito
    claims = authorizer.get('claims', {})
    if claims:
        return claims.get('sub')
    
    # From custom authorizer
    return authorizer.get('userId')
