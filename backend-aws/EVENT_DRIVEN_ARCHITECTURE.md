# Event-Driven Architecture

## Event Flow

```
S3 Upload → VideoUploaded → Step Functions (Video Processing)
API Call → PostGenerated → Lambda (Store Post)
User Action → ArticleRead → Lambda (Update Recommendations)
Platform Webhook → EngagementTracked → Step Functions (Content Learning)
```

## EventBridge Events

### VideoUploaded
**Source**: `hivemind.video`  
**Triggers**: Video Processing State Machine  
**Payload**:
```json
{
  "videoId": "uuid",
  "s3Bucket": "bucket-name",
  "s3Key": "videos/file.mp4",
  "userId": "user-123",
  "fileSize": 1048576
}
```

### PostGenerated
**Source**: `hivemind.social`  
**Triggers**: Store Post Lambda  
**Payload**:
```json
{
  "postId": "uuid",
  "brandId": "brand-123",
  "platform": "instagram",
  "content": "Post text...",
  "generatedBy": "bedrock-claude"
}
```

### ArticleRead
**Source**: `hivemind.news`  
**Triggers**: Update Recommendations Lambda  
**Payload**:
```json
{
  "articleId": "uuid",
  "userId": "user-123",
  "readDuration": 45,
  "scrollDepth": 0.8,
  "category": "tech"
}
```

### EngagementTracked
**Source**: `hivemind.social`  
**Triggers**: Content Learning State Machine  
**Payload**:
```json
{
  "postId": "uuid",
  "platform": "instagram",
  "engagementType": "like",
  "count": 150,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Step Functions Workflows

### Video Processing Pipeline
1. **ValidateVideo** - Check format and size
2. **ParallelProcessing** - Run 3 branches simultaneously:
   - Transcription (Transcribe) with polling
   - Scene Detection (Rekognition)
   - Label Detection (Rekognition)
3. **StoreResults** - Save to Aurora
4. **PublishVideoProcessed** - Emit completion event

**Duration**: ~2-5 minutes  
**Cost**: $0.025 per execution

### Content Learning Pipeline
1. **FetchEngagementData** - Get metrics from Aurora
2. **AnalyzePerformance** - Calculate engagement score
3. **IsHighPerforming?** - Branch on score > 0.7
4. **ExtractPatterns** - Use Bedrock to analyze patterns
5. **ParallelLearning** - Run 3 branches:
   - Update Embeddings (pgvector)
   - Update Recommendations
   - Train Model (incremental learning)
6. **PublishLearningComplete** - Emit completion event

**Duration**: ~30-60 seconds  
**Cost**: $0.025 per execution

## EventBridge Rules

| Rule | Event Pattern | Target |
|------|---------------|--------|
| `hivemind-video-uploaded` | `source=hivemind.video, type=VideoUploaded` | Video Processing State Machine |
| `hivemind-post-generated` | `source=hivemind.social, type=PostGenerated` | Store Post Lambda |
| `hivemind-article-read` | `source=hivemind.news, type=ArticleRead` | Update Recommendations Lambda |
| `hivemind-engagement-tracked` | `source=hivemind.social, type=EngagementTracked` | Content Learning State Machine |

## Deployment

```bash
cd backend-aws

# Deploy event-driven stack
sam build -t template-events.yaml
sam deploy --guided --template-file template-events.yaml --stack-name hivemind-events

# Test event publishing
aws events put-events --entries file://events/test-video-uploaded.json
```

## Testing Events

Create `events/test-video-uploaded.json`:
```json
{
  "Source": "hivemind.video",
  "DetailType": "VideoUploaded",
  "Detail": "{\"videoId\":\"test-123\",\"s3Bucket\":\"my-bucket\",\"s3Key\":\"videos/test.mp4\",\"userId\":\"user-1\"}",
  "EventBusName": "hivemind-bus"
}
```

Publish:
```bash
aws events put-events --entries file://events/test-video-uploaded.json
```

## Monitoring

```bash
# View state machine executions
aws stepfunctions list-executions --state-machine-arn <arn>

# View execution details
aws stepfunctions describe-execution --execution-arn <arn>

# View EventBridge metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Events \
  --metric-name Invocations \
  --dimensions Name=RuleName,Value=hivemind-video-uploaded \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

## Key Benefits

✅ **Decoupled** - Services communicate via events  
✅ **Scalable** - Each component scales independently  
✅ **Resilient** - Failed events can be retried  
✅ **Observable** - Full event history in CloudWatch  
✅ **Extensible** - Add new consumers without changing producers
