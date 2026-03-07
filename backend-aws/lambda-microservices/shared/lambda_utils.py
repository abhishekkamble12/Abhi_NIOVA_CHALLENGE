"""Shared Lambda utilities for API Gateway integration"""
import json
from typing import Any, Dict, Optional

def lambda_response(status_code: int, body: Any, headers: Optional[Dict] = None) -> Dict:
    """Create API Gateway Lambda proxy response"""
    default_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*"
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        "statusCode": status_code,
        "headers": default_headers,
        "body": json.dumps(body) if not isinstance(body, str) else body
    }

def success_response(data: Any, status_code: int = 200) -> Dict:
    """Return success response"""
    return lambda_response(status_code, data)

def error_response(message: str, status_code: int = 500) -> Dict:
    """Return error response"""
    return lambda_response(status_code, {"error": message})

def parse_body(event: Dict) -> Dict:
    """Parse request body from API Gateway event"""
    body = event.get("body", "{}")
    if isinstance(body, str):
        try:
            return json.loads(body)
        except:
            return {}
    return body

def get_path_param(event: Dict, param: str) -> Optional[str]:
    """Get path parameter from event"""
    return event.get("pathParameters", {}).get(param)

def get_query_param(event: Dict, param: str, default: Any = None) -> Any:
    """Get query parameter from event"""
    return event.get("queryStringParameters", {}).get(param, default)
