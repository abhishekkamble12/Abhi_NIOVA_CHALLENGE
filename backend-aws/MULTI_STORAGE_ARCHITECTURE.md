# Multi-Storage Architecture

## Storage Strategy

| Data Type | Storage | Reason |
|-----------|---------|--------|
| Videos, Images | **S3** | Large files, CDN integration, lifecycle policies |
| User Activity Logs | **DynamoDB** | High write throughput, TTL, fast queries by userId |
| Session Data | **DynamoDB** | Fast access, automatic expiration with TTL |
| Vector Embeddings | **OpenSearch** | k-NN search, semantic similarity |
| Relational Data | **Aurora PostgreSQL** | ACID transactions, complex queries, joins |

## Data Flow Examples

### Video Upload Workflow
```
1. Upload video → S3 (videos/)
2. Trigger Lambda → Process with Transcribe + Rekognition
3. Store scene embeddings → OpenSearch (video-scenes index)
4. Store metadata → Aurora (videos table)
5. Log activity → DynamoDB (activity table)
```

### Content Generation Workflow
```
1. Generate content → Bedrock Claude
2. Generate embedding → Bedrock Titan
3. Store embedding → OpenSearch (social-posts index)
4. Store post → Aurora (social_posts table)
5. Log activity → DynamoDB (activity table)
```

### User Activity Tracking
```
1. User reads article → API call
2. Log activity → DynamoDB (userId + timestamp)
3. Update recommendations → OpenSearch query for similar content
4. Store preference → Aurora (user_preferences table)
```

## Storage Service API

### S3 Operations
```python
from services.storage_service import upload_video_to_s3, get_presigned_url

# Upload
s3_url = upload_video_to_s3('/tmp/video.mp4', 'video-123')

# Get presigned URL
url = get_presigned_url('videos/video-123.mp4', expires_in=3600)
```

### DynamoDB Operations
```python
from services.storage_service import log_user_activity, get_user_activity

# Log activity
log_user_activity(
    user_id='user-123',
    activity_type='VIDEO_WATCHED',
    metadata={'videoId': 'video-123', 'duration': 120}
)

# Get recent activity
activities = get_user_activity('user-123', limit=50)
```

### OpenSearch Operations
```python
from services.storage_service import store_embedding, search_similar_embeddings

# Store embedding
store_embedding(
    doc_id='post-123',
    embedding=[0.1, 0.2, ...],  # 1536-dim vector
    metadata={'platform': 'instagram', 'brandId': 'brand-123'},
    index='social-posts'
)

# Search similar
results = search_similar_embeddings(
    query_embedding=[0.1, 0.2, ...],
    k=10,
    index='social-posts'
)
```

### Aurora Operations
```python
from services.storage_service import create_brand, get_brand, create_post

# Create brand
await create_brand('brand-123', 'TechCorp', 'technology')

# Get brand
brand = await get_brand('brand-123')

# Create post
await create_post(
    post_id='post-123',
    brand_id='brand-123',
    platform='instagram',
    content='Post content...',
    s3_media_url='s3://bucket/images/img.jpg'
)
```

## OpenSearch Index Setup

### Create Embedding Index
```python
from services.storage_service import create_embedding_index

# Create index with k-NN mapping
create_embedding_index(index='social-posts', dimension=1536)
create_embedding_index(index='video-scenes', dimension=1536)
create_embedding_index(index='articles', dimension=1536)
```

### Index Mappings
```json
{
  "social-posts": {
    "embedding": "knn_vector[1536]",
    "metadata": {
      "brandId": "keyword",
      "platform": "keyword",
      "topic": "text"
    }
  },
  "video-scenes": {
    "embedding": "knn_vector[1536]",
    "metadata": {
      "videoId": "keyword",
      "sceneIndex": "integer",
      "startTime": "float",
      "endTime": "float"
    }
  }
}
```

## Cost Optimization

### S3
- Use Intelligent-Tiering for automatic cost optimization
- Enable lifecycle policies to move old videos to Glacier
- Use CloudFront for CDN to reduce data transfer costs

### DynamoDB
- Use on-demand billing for unpredictable workloads
- Enable TTL to auto-delete old activity logs (30 days)
- Use GSI sparingly to avoid extra costs

### OpenSearch
- Start with t3.small.search (1 node) for development
- Scale to r6g.large.search for production
- Use UltraWarm for infrequently accessed embeddings

### Aurora
- Use Serverless v2 with 0.5-2 ACU range
- Enable auto-pause for development environments
- Use read replicas only when needed

## Deployment

```bash
# Deploy storage stack
sam build -t template-storage.yaml
sam deploy --guided --template-file template-storage.yaml --stack-name hivemind-storage

# Initialize Aurora schema
psql -h <aurora-endpoint> -U hivemind -d hiveminddb -f schema-aurora.sql

# Create OpenSearch indexes
python -c "from services.storage_service import create_embedding_index; create_embedding_index('social-posts'); create_embedding_index('video-scenes')"
```

## Environment Variables

```bash
AWS_REGION=ap-south-1
S3_BUCKET=hivemind-media-{account-id}
DYNAMODB_ACTIVITY_TABLE=hivemind-activity
OPENSEARCH_ENDPOINT=search-hivemind-embeddings-xxx.ap-south-1.es.amazonaws.com
AURORA_HOST=hivemind-cluster.cluster-xxx.ap-south-1.rds.amazonaws.com
AURORA_DB=hiveminddb
AURORA_USER=hivemind
AURORA_PASSWORD=<secret>
```

## Monitoring

```bash
# S3 metrics
aws cloudwatch get-metric-statistics --namespace AWS/S3 --metric-name NumberOfObjects

# DynamoDB metrics
aws cloudwatch get-metric-statistics --namespace AWS/DynamoDB --metric-name ConsumedReadCapacityUnits

# OpenSearch metrics
aws cloudwatch get-metric-statistics --namespace AWS/ES --metric-name SearchRate

# Aurora metrics
aws cloudwatch get-metric-statistics --namespace AWS/RDS --metric-name DatabaseConnections
```
