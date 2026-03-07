# HiveMind Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
│  Next.js Frontend (S3 + CloudFront)                                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (REST)                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  POST   /social/brands          → social_create_brand        │  │
│  │  GET    /social/brands          → social_list_brands         │  │
│  │  GET    /social/brands/{id}     → social_get_brand           │  │
│  │  GET    /social/posts/{id}      → social_get_post            │  │
│  │  POST   /social/generate        → social_generate_content    │  │
│  │  GET    /feed/personalized/{id} → feed_personalized          │  │
│  │  POST   /videos/upload          → video_upload_handler       │  │
│  │  POST   /ai/generate            → ai_generate_content        │  │
│  │  POST   /ai/video/process       → ai_process_video           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │ AWS_PROXY Integration
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      LAMBDA FUNCTIONS                                │
│  ┌─────────────────────┐  ┌─────────────────────────────────────┐  │
│  │  API Functions (9)  │  │  Step Functions Handlers (7)        │  │
│  │  ─────────────────  │  │  ───────────────────────────────    │  │
│  │  • social_*         │  │  • stepfunctions_validate_video     │  │
│  │  • feed_*           │  │  • stepfunctions_start_transcription│  │
│  │  • video_*          │  │  • stepfunctions_check_transcription│  │
│  │  • ai_*             │  │  • stepfunctions_detect_scenes      │  │
│  │                     │  │  • stepfunctions_detect_labels      │  │
│  │                     │  │  • stepfunctions_check_rekognition  │  │
│  │                     │  │  • stepfunctions_store_video_results│  │
│  └─────────────────────┘  └─────────────────────────────────────┘  │
│                                                                      │
│  Runtime: Python 3.11 | Memory: 512MB | Timeout: 300s              │
└────────────────────────────┬────────────────────────────────────────┘
                             │ Shared Dependencies
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      LAMBDA LAYER                                    │
│  • boto3 >= 1.34.0                                                  │
│  • botocore >= 1.34.0                                               │
│  • psycopg2-binary (PostgreSQL driver)                             │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                               │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  AWS Step Functions: Video Processing Pipeline               │ │
│  │                                                               │ │
│  │  ValidateVideo                                                │ │
│  │       ↓                                                       │ │
│  │  ParallelProcessing                                           │ │
│  │       ├─→ Transcription Branch                               │ │
│  │       │   ├─ StartTranscription                              │ │
│  │       │   ├─ Wait (30s)                                      │ │
│  │       │   ├─ CheckTranscription                              │ │
│  │       │   └─ Loop until complete                             │ │
│  │       │                                                       │ │
│  │       ├─→ Scene Detection Branch                             │ │
│  │       │   ├─ DetectScenes                                    │ │
│  │       │   ├─ Wait (30s)                                      │ │
│  │       │   ├─ CheckRekognition                                │ │
│  │       │   └─ Loop until complete                             │ │
│  │       │                                                       │ │
│  │       └─→ Label Detection Branch                             │ │
│  │           ├─ DetectLabels                                    │ │
│  │           ├─ Wait (30s)                                      │ │
│  │           ├─ CheckRekognition                                │ │
│  │           └─ Loop until complete                             │ │
│  │       ↓                                                       │ │
│  │  StoreResults (aggregate all branches)                       │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      AWS SERVICES LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  S3 Storage  │  │   Bedrock    │  │  Transcribe  │             │
│  │  ──────────  │  │  ──────────  │  │  ──────────  │             │
│  │  • Videos    │  │  • Titan     │  │  • Audio     │             │
│  │  • Images    │  │    Embeddings│  │    to Text   │             │
│  │  • Media     │  │  • Claude 3  │  │              │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Rekognition  │  │  DynamoDB    │  │   Aurora     │             │
│  │ ──────────── │  │  ──────────  │  │  PostgreSQL  │             │
│  │  • Scene     │  │  • User      │  │  ──────────  │             │
│  │    Detection │  │    Activity  │  │  • Brands    │             │
│  │  • Labels    │  │  • Sessions  │  │  • Posts     │             │
│  │              │  │              │  │  • Videos    │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                      │
│  ┌──────────────┐                                                   │
│  │  OpenSearch  │                                                   │
│  │  ──────────  │                                                   │
│  │  • Vector    │                                                   │
│  │    Embeddings│                                                   │
│  │  • Semantic  │                                                   │
│  │    Search    │                                                   │
│  └──────────────┘                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Social Media Content Generation

```
User Request
    ↓
API Gateway: POST /social/generate
    ↓
Lambda: social_generate_content
    ↓
Bedrock: Claude 3 (text generation)
    ↓
Aurora: Store generated post
    ↓
Response: Generated content
```

### 2. Video Processing Pipeline

```
Video Upload to S3
    ↓
S3 Event → EventBridge
    ↓
Step Functions: Start Execution
    ↓
ValidateVideo (check size, format)
    ↓
Parallel Processing:
    ├─ Transcribe: Audio → Text
    ├─ Rekognition: Scene Detection
    └─ Rekognition: Label Detection
    ↓
StoreResults: Save to Aurora
    ↓
Complete
```

### 3. Personalized Feed

```
User Request
    ↓
API Gateway: GET /feed/personalized/{userId}
    ↓
Lambda: feed_personalized
    ↓
DynamoDB: Get user preferences
    ↓
OpenSearch: Vector similarity search
    ↓
Aurora: Get article details
    ↓
Response: Personalized feed
```

## IAM Permissions

### Lambda Execution Role

```
Permissions:
- CloudWatch Logs (write)
- S3 (read/write on media-ai-content)
- Bedrock (invoke models)
- Transcribe (start/get jobs)
- Rekognition (detect labels/scenes)
- DynamoDB (read/write on hivemind-*)
- Aurora (via VPC/security groups)
```

### Step Functions Role

```
Permissions:
- Lambda (invoke hivemind-stepfunctions-*)
```

## Network Architecture

```
┌─────────────────────────────────────────┐
│  VPC (10.0.0.0/16)                      │
│  ┌───────────────────────────────────┐  │
│  │  Private Subnet 1 (10.0.1.0/24)   │  │
│  │  - Aurora Primary                  │  │
│  │  - OpenSearch Node 1               │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Private Subnet 2 (10.0.2.0/24)   │  │
│  │  - Aurora Replica                  │  │
│  │  - OpenSearch Node 2               │  │
│  └───────────────────────────────────┘  │
│                                          │
│  Lambda Functions (VPC-attached)        │
└─────────────────────────────────────────┘
```

## Deployment Components

| Component | Count | Purpose |
|-----------|-------|---------|
| Lambda Functions | 16 | API handlers + Step Functions |
| Lambda Layer | 1 | Shared dependencies |
| API Gateway | 1 | REST API with 9 routes |
| Step Functions | 1 | Video processing workflow |
| IAM Roles | 2 | Lambda + Step Functions |
| S3 Buckets | 2 | Media storage + Frontend |
| DynamoDB Tables | 2 | User activity + Sessions |
| Aurora Cluster | 1 | Relational data |
| OpenSearch Domain | 1 | Vector embeddings |

## Scalability

- **Lambda**: Auto-scales to 1000 concurrent executions
- **API Gateway**: 10,000 requests/second
- **Step Functions**: 4,000 executions/second
- **Aurora Serverless v2**: 0.5-2 ACU (auto-scaling)
- **DynamoDB**: On-demand (auto-scaling)
- **OpenSearch**: 2-node Multi-AZ

## Cost Optimization

- Lambda: Pay per invocation + duration
- API Gateway: Pay per request
- Step Functions: Pay per state transition
- Aurora: Pay per ACU-hour (scales to zero)
- S3: Lifecycle policies for old media
- CloudWatch: Log retention policies

## Security

- **Encryption at Rest**: All data encrypted (KMS)
- **Encryption in Transit**: TLS 1.2+
- **IAM**: Least privilege access
- **VPC**: Private subnets for databases
- **API Gateway**: CORS enabled
- **Secrets**: AWS Secrets Manager for credentials
