"""Multi-storage service layer for HiveMind"""
import json
import os
import boto3
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncpg
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# Clients
s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'ap-south-1'))
dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'ap-south-1'))

# Environment
S3_BUCKET = os.getenv('S3_BUCKET')
DYNAMODB_ACTIVITY_TABLE = os.getenv('DYNAMODB_ACTIVITY_TABLE', 'hivemind-activity')
OPENSEARCH_ENDPOINT = os.getenv('OPENSEARCH_ENDPOINT')
AURORA_HOST = os.getenv('AURORA_HOST')
AURORA_DB = os.getenv('AURORA_DB', 'hiveminddb')
AURORA_USER = os.getenv('AURORA_USER', 'hivemind')
AURORA_PASSWORD = os.getenv('AURORA_PASSWORD')


# ==================== S3 - Media Storage ====================

def upload_video_to_s3(file_path: str, video_id: str) -> str:
    """Upload video to S3"""
    s3_key = f'videos/{video_id}.mp4'
    s3.upload_file(file_path, S3_BUCKET, s3_key)
    return f's3://{S3_BUCKET}/{s3_key}'


def upload_image_to_s3(file_bytes: bytes, image_id: str) -> str:
    """Upload image to S3"""
    s3_key = f'images/{image_id}.jpg'
    s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=file_bytes)
    return f's3://{S3_BUCKET}/{s3_key}'


def get_presigned_url(s3_key: str, expires_in: int = 3600) -> str:
    """Generate presigned URL for media access"""
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': S3_BUCKET, 'Key': s3_key},
        ExpiresIn=expires_in
    )


# ==================== DynamoDB - User Activity ====================

def log_user_activity(user_id: str, activity_type: str, metadata: Dict[str, Any]):
    """Log user activity to DynamoDB"""
    table = dynamodb.Table(DYNAMODB_ACTIVITY_TABLE)
    table.put_item(Item={
        'userId': user_id,
        'timestamp': datetime.utcnow().isoformat(),
        'activityType': activity_type,
        'metadata': metadata,
        'ttl': int(datetime.utcnow().timestamp()) + 2592000  # 30 days
    })


def get_user_activity(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent user activity from DynamoDB"""
    table = dynamodb.Table(DYNAMODB_ACTIVITY_TABLE)
    response = table.query(
        KeyConditionExpression='userId = :uid',
        ExpressionAttributeValues={':uid': user_id},
        ScanIndexForward=False,
        Limit=limit
    )
    return response['Items']


def store_session(session_id: str, user_id: str, data: Dict[str, Any]):
    """Store session data in DynamoDB"""
    table = dynamodb.Table('hivemind-sessions')
    table.put_item(Item={
        'sessionId': session_id,
        'userId': user_id,
        'data': data,
        'createdAt': datetime.utcnow().isoformat(),
        'ttl': int(datetime.utcnow().timestamp()) + 86400  # 24 hours
    })


# ==================== OpenSearch - Vector Embeddings ====================

def get_opensearch_client() -> OpenSearch:
    """Initialize OpenSearch client with IAM auth"""
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        os.getenv('AWS_REGION', 'ap-south-1'),
        'es',
        session_token=credentials.token
    )
    
    return OpenSearch(
        hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )


def store_embedding(doc_id: str, embedding: List[float], metadata: Dict[str, Any], index: str = 'embeddings'):
    """Store embedding in OpenSearch"""
    client = get_opensearch_client()
    
    document = {
        'embedding': embedding,
        'metadata': metadata,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    client.index(index=index, id=doc_id, body=document)


def search_similar_embeddings(query_embedding: List[float], k: int = 10, index: str = 'embeddings') -> List[Dict[str, Any]]:
    """Search for similar embeddings using k-NN"""
    client = get_opensearch_client()
    
    query = {
        'size': k,
        'query': {
            'knn': {
                'embedding': {
                    'vector': query_embedding,
                    'k': k
                }
            }
        }
    }
    
    response = client.search(index=index, body=query)
    return [hit['_source'] for hit in response['hits']['hits']]


def create_embedding_index(index: str = 'embeddings', dimension: int = 1024):
    """Create OpenSearch index with k-NN mapping"""
    client = get_opensearch_client()
    
    mapping = {
        'settings': {
            'index': {
                'knn': True,
                'knn.algo_param.ef_search': 512
            }
        },
        'mappings': {
            'properties': {
                'embedding': {
                    'type': 'knn_vector',
                    'dimension': dimension,
                    'method': {
                        'name': 'hnsw',
                        'space_type': 'cosinesimil',
                        'engine': 'nmslib'
                    }
                },
                'metadata': {'type': 'object'},
                'timestamp': {'type': 'date'}
            }
        }
    }
    
    client.indices.create(index=index, body=mapping)


# ==================== Aurora PostgreSQL - Relational Data ====================

async def get_aurora_connection():
    """Get Aurora PostgreSQL connection"""
    return await asyncpg.connect(
        host=AURORA_HOST,
        database=AURORA_DB,
        user=AURORA_USER,
        password=AURORA_PASSWORD
    )


async def create_brand(brand_id: str, name: str, industry: str) -> Dict[str, Any]:
    """Create brand in Aurora"""
    conn = await get_aurora_connection()
    try:
        await conn.execute(
            'INSERT INTO brands (id, name, industry, created_at) VALUES ($1, $2, $3, $4)',
            brand_id, name, industry, datetime.utcnow()
        )
        return {'id': brand_id, 'name': name, 'industry': industry}
    finally:
        await conn.close()


async def get_brand(brand_id: str) -> Optional[Dict[str, Any]]:
    """Get brand from Aurora"""
    conn = await get_aurora_connection()
    try:
        row = await conn.fetchrow('SELECT * FROM brands WHERE id = $1', brand_id)
        return dict(row) if row else None
    finally:
        await conn.close()


async def create_post(post_id: str, brand_id: str, platform: str, content: str, s3_media_url: Optional[str] = None):
    """Create social post in Aurora"""
    conn = await get_aurora_connection()
    try:
        await conn.execute(
            'INSERT INTO social_posts (id, brand_id, platform, content, media_url, created_at) VALUES ($1, $2, $3, $4, $5, $6)',
            post_id, brand_id, platform, content, s3_media_url, datetime.utcnow()
        )
    finally:
        await conn.close()


async def get_post_analytics(post_id: str) -> Dict[str, Any]:
    """Get post analytics from Aurora"""
    conn = await get_aurora_connection()
    try:
        row = await conn.fetchrow(
            'SELECT p.*, e.likes, e.comments, e.shares FROM social_posts p LEFT JOIN engagement e ON p.id = e.post_id WHERE p.id = $1',
            post_id
        )
        return dict(row) if row else {}
    finally:
        await conn.close()


async def store_video_metadata(video_id: str, s3_url: str, duration: float, transcription: Optional[str] = None):
    """Store video metadata in Aurora"""
    conn = await get_aurora_connection()
    try:
        await conn.execute(
            'INSERT INTO videos (id, s3_url, duration, transcription, created_at) VALUES ($1, $2, $3, $4, $5)',
            video_id, s3_url, duration, transcription, datetime.utcnow()
        )
    finally:
        await conn.close()
