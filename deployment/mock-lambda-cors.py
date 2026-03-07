import json

def handler(event, context):
    """Mock Lambda with CORS headers"""
    
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    # Handle OPTIONS (preflight)
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Mock response
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'message': 'Success',
            'data': [],
            'note': 'This is a mock response with CORS headers. Database not configured yet.'
        })
    }
