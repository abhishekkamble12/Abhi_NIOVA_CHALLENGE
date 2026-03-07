# AWS AI Services Lambda Deployment

## Architecture

**Replaced Local Libraries:**
- ❌ SentenceTransformers → ✅ Amazon Bedrock Titan Embeddings (1536-dim)
- ❌ Local LLM → ✅ Amazon Bedrock Claude 3 Sonnet
- ❌ Whisper/Local STT → ✅ Amazon Transcribe
- ❌ Local CV models → ✅ Amazon Rekognition

## Lambda Functions

### 1. `ai_generate_content` - Social Media Generation
- **Trigger**: API Gateway POST `/ai/generate`
- **Input**: `{platform, topic, tone}`
- **Services**: Bedrock Claude 3 + Titan Embeddings
- **Output**: Generated content + embeddings

### 2. `ai_process_video` - Video Intelligence
- **Trigger**: S3 upload to `videos/` OR API POST `/ai/video/process`
- **Input**: S3 bucket + key
- **Services**: Transcribe + Rekognition (scenes + labels)
- **Output**: Transcription job, scenes, labels

### 3. `ai_analyze_article` - News Analysis
- **Trigger**: API POST `/ai/article/analyze`
- **Input**: `{action: "analyze", text, title}` OR `{action: "search", query}`
- **Services**: Bedrock Titan Embeddings + Claude 3
- **Output**: Embeddings, summary, topics

### 4. `ai_analyze_image` - Image Intelligence
- **Trigger**: S3 upload to `images/` OR API POST `/ai/image/analyze`
- **Input**: S3 bucket + key
- **Services**: Rekognition + Bedrock Claude 3
- **Output**: Labels, text detection, AI caption

## Deployment

```bash
cd lambda-microservices

# Deploy with SAM
sam build -t template-ai.yaml
sam deploy --guided --template-file template-ai.yaml
```

## IAM Permissions

Each Lambda has:
- `bedrock:InvokeModel` - All Bedrock models
- `transcribe:*TranscriptionJob` - Audio transcription
- `rekognition:Detect*` + `rekognition:*Detection` - Video/image analysis
- `s3:GetObject` + `s3:PutObject` - Media access

## Environment Variables

```bash
AWS_REGION=ap-south-1
S3_BUCKET=hivemind-media-{account-id}
```

## Cost Estimates (per 1M requests)

| Service | Usage | Cost |
|---------|-------|------|
| Bedrock Titan Embeddings | 1M calls | $0.10 |
| Bedrock Claude 3 Sonnet | 1M tokens | $3.00 |
| Transcribe | 100 hours | $144 |
| Rekognition Video | 100 hours | $120 |
| Lambda | 1M invocations | $10 |

## Testing

```bash
# Generate content
curl -X POST https://{api-id}.execute-api.ap-south-1.amazonaws.com/Prod/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"platform":"instagram","topic":"AI innovation","tone":"excited"}'

# Analyze article
curl -X POST https://{api-id}.execute-api.ap-south-1.amazonaws.com/Prod/ai/article/analyze \
  -H "Content-Type: application/json" \
  -d '{"action":"analyze","title":"AI News","text":"Article content..."}'

# Process video (upload to S3 triggers automatically)
aws s3 cp video.mp4 s3://hivemind-media-{account-id}/videos/video.mp4
```

## Key Advantages

✅ **No model management** - Fully managed AWS services  
✅ **Auto-scaling** - Lambda scales to zero  
✅ **Pay-per-use** - No idle costs  
✅ **Enterprise-grade** - AWS SLAs and security  
✅ **Event-driven** - S3 triggers for automatic processing
