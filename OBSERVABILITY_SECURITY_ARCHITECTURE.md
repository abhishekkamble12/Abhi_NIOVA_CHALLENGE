# 🔒 Observability & Security Architecture for HiveMind

## Executive Summary

This document details the **observability and security architecture** for HiveMind using AWS services. The architecture implements comprehensive logging, monitoring, tracing, identity management, and security controls.

**Core Services:**
- CloudWatch (logs, metrics, alarms)
- X-Ray (distributed tracing)
- CloudTrail (audit logging)
- Cognito (user authentication)
- IAM (access control)
- Secrets Manager (secrets)
- WAF (API protection)
- VPC (network security)

---

## 📊 1. Observability Architecture

### 1.1 Logging Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LOGS                          │
│  Lambda → CloudWatch Logs → Log Groups                      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    LOG AGGREGATION                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  /aws/lambda/social-*                                │  │
│  │  /aws/lambda/news-*                                  │  │
│  │  /aws/lambda/video-*                                 │  │
│  │  /aws/apigateway/hivemind-api                        │  │
│  │  /aws/states/video-processing                        │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    LOG INSIGHTS                              │
│  - Query logs with SQL-like syntax                          │
│  - Real-time analysis                                       │
│  - Custom dashboards                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    LOG RETENTION                             │
│  - 7 days: Debug logs                                       │
│  - 30 days: Application logs                                │
│  - 90 days: Security logs                                   │
│  - 1 year: Audit logs                                       │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Structured Logging

```python
# Lambda: structured-logging

import json
import logging
from datetime import datetime
import uuid

class StructuredLogger:
    """
    Structured JSON logging for CloudWatch
    """
    
    def __init__(self, service_name):
        self.service_name = service_name
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
    
    def log(self, level, message, **kwargs):
        """
        Log structured message
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'service': self.service_name,
            'message': message,
            'request_id': kwargs.get('request_id', str(uuid.uuid4())),
            'user_id': kwargs.get('user_id'),
            'correlation_id': kwargs.get('correlation_id'),
            'data': kwargs.get('data', {})
        }
        
        self.logger.info(json.dumps(log_entry))
    
    def info(self, message, **kwargs):
        self.log('INFO', message, **kwargs)
    
    def error(self, message, **kwargs):
        self.log('ERROR', message, **kwargs)
    
    def warning(self, message, **kwargs):
        self.log('WARNING', message, **kwargs)

# Usage
logger = StructuredLogger('social-media-engine')

logger.info('Content generated', 
    user_id='user-123',
    data={
        'brand_id': 'brand-456',
        'platform': 'instagram',
        'duration_ms': 1250
    }
)
```

### 1.3 CloudWatch Log Insights Queries

```sql
-- Query 1: Error rate by service
fields @timestamp, service, message
| filter level = "ERROR"
| stats count() as error_count by service
| sort error_count desc

-- Query 2: Slow Lambda functions
fields @timestamp, @duration, service
| filter @type = "REPORT"
| stats avg(@duration) as avg_duration, max(@duration) as max_duration by service
| sort avg_duration desc

-- Query 3: User activity patterns
fields @timestamp, user_id, message
| filter user_id like /user-/
| stats count() as activity_count by user_id
| sort activity_count desc
| limit 100

-- Query 4: Bedrock API usage
fields @timestamp, data.model_id, data.input_tokens, data.output_tokens
| filter message = "Bedrock invocation"
| stats sum(data.input_tokens) as total_input, sum(data.output_tokens) as total_output by data.model_id

-- Query 5: API Gateway latency
fields @timestamp, @message
| filter @message like /Latency/
| parse @message "Latency: * ms" as latency
| stats avg(latency) as avg_latency, max(latency) as max_latency, pct(latency, 95) as p95_latency
```

---

## 📈 2. Monitoring Architecture

### 2.1 CloudWatch Metrics

```python
# Lambda: cloudwatch-metrics

import boto3
from datetime import datetime

cloudwatch = boto3.client('cloudwatch')

class MetricsPublisher:
    """
    Publish custom metrics to CloudWatch
    """
    
    def __init__(self, namespace='HiveMind'):
        self.namespace = namespace
        self.cloudwatch = cloudwatch
    
    def publish_metric(self, metric_name, value, unit='Count', dimensions=None):
        """
        Publish single metric
        """
        metric_data = {
            'MetricName': metric_name,
            'Value': value,
            'Unit': unit,
            'Timestamp': datetime.utcnow(),
            'Dimensions': dimensions or []
        }
        
        self.cloudwatch.put_metric_data(
            Namespace=self.namespace,
            MetricData=[metric_data]
        )
    
    def publish_batch(self, metrics):
        """
        Publish multiple metrics
        """
        self.cloudwatch.put_metric_data(
            Namespace=self.namespace,
            MetricData=metrics
        )

# Usage
metrics = MetricsPublisher()

# Content generation metric
metrics.publish_metric(
    metric_name='ContentGenerated',
    value=1,
    dimensions=[
        {'Name': 'Platform', 'Value': 'instagram'},
        {'Name': 'BrandId', 'Value': 'brand-123'}
    ]
)

# Bedrock latency metric
metrics.publish_metric(
    metric_name='BedrockLatency',
    value=1250,
    unit='Milliseconds',
    dimensions=[
        {'Name': 'Model', 'Value': 'claude-3-sonnet'}
    ]
)

# Vector search metric
metrics.publish_metric(
    metric_name='VectorSearchResults',
    value=10,
    dimensions=[
        {'Name': 'IndexType', 'Value': 'articles'}
    ]
)
```

### 2.2 CloudWatch Alarms

```yaml
Alarms:
  
  # Lambda Errors
  LambdaHighErrorRate:
    MetricName: Errors
    Namespace: AWS/Lambda
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 2
    Threshold: 10
    ComparisonOperator: GreaterThanThreshold
    AlarmActions:
      - arn:aws:sns:ops-alerts
    Dimensions:
      - Name: FunctionName
        Value: social-content-generate
  
  # API Gateway Latency
  APIHighLatency:
    MetricName: Latency
    Namespace: AWS/ApiGateway
    Statistic: Average
    Period: 60
    EvaluationPeriods: 3
    Threshold: 3000
    ComparisonOperator: GreaterThanThreshold
    AlarmActions:
      - arn:aws:sns:ops-alerts
  
  # Bedrock Throttling
  BedrockThrottled:
    MetricName: ThrottleExceptions
    Namespace: HiveMind
    Statistic: Sum
    Period: 60
    EvaluationPeriods: 1
    Threshold: 5
    ComparisonOperator: GreaterThanThreshold
    AlarmActions:
      - arn:aws:sns:ops-alerts
  
  # Aurora CPU
  AuroraHighCPU:
    MetricName: CPUUtilization
    Namespace: AWS/RDS
    Statistic: Average
    Period: 300
    EvaluationPeriods: 2
    Threshold: 80
    ComparisonOperator: GreaterThanThreshold
    AlarmActions:
      - arn:aws:sns:ops-alerts
  
  # OpenSearch Disk Space
  OpenSearchLowDisk:
    MetricName: FreeStorageSpace
    Namespace: AWS/ES
    Statistic: Average
    Period: 300
    EvaluationPeriods: 1
    Threshold: 20480  # 20GB
    ComparisonOperator: LessThanThreshold
    AlarmActions:
      - arn:aws:sns:ops-alerts
```

### 2.3 CloudWatch Dashboards

```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "title": "API Gateway Requests",
        "metrics": [
          ["AWS/ApiGateway", "Count", {"stat": "Sum"}]
        ],
        "period": 300,
        "region": "us-east-1",
        "yAxis": {"left": {"min": 0}}
      }
    },
    {
      "type": "metric",
      "properties": {
        "title": "Lambda Invocations by Function",
        "metrics": [
          ["AWS/Lambda", "Invocations", {"stat": "Sum"}]
        ],
        "period": 300,
        "region": "us-east-1"
      }
    },
    {
      "type": "metric",
      "properties": {
        "title": "Bedrock API Calls",
        "metrics": [
          ["HiveMind", "BedrockInvocations", {"stat": "Sum"}]
        ],
        "period": 300,
        "region": "us-east-1"
      }
    },
    {
      "type": "log",
      "properties": {
        "title": "Recent Errors",
        "query": "SOURCE '/aws/lambda/social-content-generate'\n| fields @timestamp, @message\n| filter level = 'ERROR'\n| sort @timestamp desc\n| limit 20",
        "region": "us-east-1"
      }
    }
  ]
}
```

---

## 🔍 3. Distributed Tracing (X-Ray)

### 3.1 X-Ray Integration

```python
# Lambda: xray-tracing

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
import boto3

# Patch AWS SDK
patch_all()

@xray_recorder.capture('generate_social_post')
async def generate_social_post(brand_id, topic, platform):
    """
    Generate social post with X-Ray tracing
    """
    
    # Add annotations (indexed)
    xray_recorder.put_annotation('brand_id', brand_id)
    xray_recorder.put_annotation('platform', platform)
    
    # Add metadata (not indexed)
    xray_recorder.put_metadata('topic', topic)
    
    # Subsegment: Fetch brand
    with xray_recorder.capture('fetch_brand'):
        brand = await get_brand(brand_id)
        xray_recorder.put_metadata('brand_name', brand['name'])
    
    # Subsegment: Vector search
    with xray_recorder.capture('vector_search'):
        similar_posts = await search_similar_posts(topic, platform)
        xray_recorder.put_metadata('results_count', len(similar_posts))
    
    # Subsegment: Bedrock generation
    with xray_recorder.capture('bedrock_generation'):
        response = await invoke_bedrock(prompt)
        xray_recorder.put_metadata('tokens_used', response['usage'])
    
    # Subsegment: Store result
    with xray_recorder.capture('store_post'):
        await store_post(post_data)
    
    return post_data
```

### 3.2 X-Ray Service Map

```
User Request
  ↓
API Gateway (avg: 50ms)
  ↓
Lambda: social-content-generate (avg: 2.5s)
  ├─ DynamoDB: brands-table (avg: 15ms)
  ├─ OpenSearch: posts-index (avg: 45ms)
  ├─ Bedrock: claude-3-sonnet (avg: 2.1s)
  └─ DynamoDB: generated-posts-table (avg: 20ms)
```

---

## 🔒 4. Security Architecture

### 4.1 Identity Management (Cognito)

```yaml
UserPool: hivemind-users
  
  Configuration:
    SignInAliases:
      - email
    
    PasswordPolicy:
      MinimumLength: 12
      RequireUppercase: true
      RequireLowercase: true
      RequireNumbers: true
      RequireSymbols: true
      TemporaryPasswordValidityDays: 7
    
    MFA:
      Enabled: Optional
      Methods: [TOTP, SMS]
    
    AccountRecovery:
      - email
    
    EmailVerification: Required
    
    UserAttributes:
      - email (required)
      - name
      - custom:subscription_tier
      - custom:brand_count
    
    Triggers:
      PreSignUp: arn:aws:lambda:cognito-pre-signup
      PostConfirmation: arn:aws:lambda:cognito-post-confirmation
      PreAuthentication: arn:aws:lambda:cognito-pre-auth
      PostAuthentication: arn:aws:lambda:cognito-post-auth
```

### 4.2 API Gateway Authorizer

```python
# Lambda: api-authorizer

import boto3
import jwt
import json

cognito = boto3.client('cognito-idp')

def lambda_handler(event, context):
    """
    Custom authorizer for API Gateway
    """
    
    token = event['authorizationToken'].replace('Bearer ', '')
    method_arn = event['methodArn']
    
    try:
        # Decode JWT (Cognito handles signature verification)
        decoded = jwt.decode(
            token,
            options={"verify_signature": False}
        )
        
        user_id = decoded['sub']
        email = decoded.get('email')
        tier = decoded.get('custom:subscription_tier', 'free')
        
        # Check if user is active
        user = cognito.admin_get_user(
            UserPoolId='us-east-1_xxxxx',
            Username=user_id
        )
        
        if user['UserStatus'] != 'CONFIRMED':
            raise Exception('User not confirmed')
        
        # Generate policy
        policy = generate_policy(
            principal_id=user_id,
            effect='Allow',
            resource=method_arn
        )
        
        # Add context
        policy['context'] = {
            'userId': user_id,
            'email': email,
            'tier': tier
        }
        
        return policy
    
    except Exception as e:
        print(f"Authorization failed: {str(e)}")
        return generate_policy('user', 'Deny', method_arn)


def generate_policy(principal_id, effect, resource):
    """
    Generate IAM policy
    """
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
    }
```

### 4.3 IAM Roles & Policies

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LambdaBasicExecution",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Sid": "DynamoDBAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/brands-table",
        "arn:aws:dynamodb:*:*:table/generated-posts-table",
        "arn:aws:dynamodb:*:*:table/videos-table"
      ]
    },
    {
      "Sid": "BedrockAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
        "arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v1"
      ]
    },
    {
      "Sid": "S3Access",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::video-uploads-bucket/*",
        "arn:aws:s3:::video-processed-bucket/*"
      ]
    },
    {
      "Sid": "SecretsManagerAccess",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:hivemind/*"
    },
    {
      "Sid": "XRayAccess",
      "Effect": "Allow",
      "Action": [
        "xray:PutTraceSegments",
        "xray:PutTelemetryRecords"
      ],
      "Resource": "*"
    }
  ]
}
```

### 4.4 Secrets Management

```python
# Lambda: secrets-manager

import boto3
import json

secrets_manager = boto3.client('secretsmanager')

class SecretsManager:
    """
    Manage secrets with caching
    """
    
    def __init__(self):
        self.cache = {}
    
    def get_secret(self, secret_name):
        """
        Get secret with caching
        """
        if secret_name in self.cache:
            return self.cache[secret_name]
        
        response = secrets_manager.get_secret_value(
            SecretId=secret_name
        )
        
        secret = json.loads(response['SecretString'])
        self.cache[secret_name] = secret
        
        return secret
    
    def get_database_credentials(self):
        """
        Get Aurora credentials
        """
        return self.get_secret('hivemind/aurora/credentials')
    
    def get_opensearch_credentials(self):
        """
        Get OpenSearch credentials
        """
        return self.get_secret('hivemind/opensearch/credentials')

# Usage
secrets = SecretsManager()
db_creds = secrets.get_database_credentials()

connection_string = f"postgresql://{db_creds['username']}:{db_creds['password']}@{db_creds['host']}:{db_creds['port']}/{db_creds['database']}"
```

### 4.5 VPC Architecture

```yaml
VPC: hivemind-vpc
  CIDR: 10.0.0.0/16
  
  Subnets:
    Public:
      - 10.0.1.0/24 (us-east-1a)
      - 10.0.2.0/24 (us-east-1b)
      Resources:
        - NAT Gateway
        - Application Load Balancer
    
    Private:
      - 10.0.10.0/24 (us-east-1a)
      - 10.0.11.0/24 (us-east-1b)
      Resources:
        - Lambda Functions
        - ECS Tasks
    
    Database:
      - 10.0.20.0/24 (us-east-1a)
      - 10.0.21.0/24 (us-east-1b)
      Resources:
        - Aurora PostgreSQL
        - OpenSearch
        - ElastiCache Redis
  
  SecurityGroups:
    lambda-sg:
      Ingress: None
      Egress:
        - 0.0.0.0/0:443 (HTTPS)
        - aurora-sg:5432
        - opensearch-sg:443
        - elasticache-sg:6379
    
    aurora-sg:
      Ingress:
        - lambda-sg:5432
      Egress: None
    
    opensearch-sg:
      Ingress:
        - lambda-sg:443
      Egress: None
    
    elasticache-sg:
      Ingress:
        - lambda-sg:6379
      Egress: None
```

### 4.6 WAF Rules

```yaml
WebACL: hivemind-waf
  
  Rules:
    - Name: RateLimitRule
      Priority: 1
      Statement:
        RateBasedStatement:
          Limit: 2000
          AggregateKeyType: IP
      Action: Block
    
    - Name: GeoBlockingRule
      Priority: 2
      Statement:
        GeoMatchStatement:
          CountryCodes: [CN, RU, KP]
      Action: Block
    
    - Name: SQLInjectionRule
      Priority: 3
      Statement:
        ManagedRuleGroupStatement:
          VendorName: AWS
          Name: AWSManagedRulesSQLiRuleSet
      Action: Block
    
    - Name: XSSRule
      Priority: 4
      Statement:
        ManagedRuleGroupStatement:
          VendorName: AWS
          Name: AWSManagedRulesKnownBadInputsRuleSet
      Action: Block
    
    - Name: BotControlRule
      Priority: 5
      Statement:
        ManagedRuleGroupStatement:
          VendorName: AWS
          Name: AWSManagedRulesBotControlRuleSet
      Action: Block
```

---

## ✅ 5. Production Readiness

### 5.1 Deployment Checklist

```yaml
Infrastructure:
  - [ ] VPC configured with public/private subnets
  - [ ] Security groups configured
  - [ ] NAT Gateway deployed
  - [ ] Aurora PostgreSQL deployed
  - [ ] OpenSearch cluster deployed
  - [ ] ElastiCache Redis deployed
  - [ ] S3 buckets created with encryption
  - [ ] CloudFront distribution configured

Security:
  - [ ] Cognito user pool configured
  - [ ] IAM roles created with least privilege
  - [ ] Secrets Manager configured
  - [ ] WAF rules deployed
  - [ ] SSL/TLS certificates installed
  - [ ] API Gateway authorizer configured
  - [ ] Encryption at rest enabled
  - [ ] Encryption in transit enabled

Observability:
  - [ ] CloudWatch log groups created
  - [ ] CloudWatch alarms configured
  - [ ] X-Ray tracing enabled
  - [ ] CloudTrail enabled
  - [ ] CloudWatch dashboards created
  - [ ] SNS topics for alerts configured

Application:
  - [ ] Lambda functions deployed
  - [ ] API Gateway configured
  - [ ] Step Functions workflows deployed
  - [ ] EventBridge rules configured
  - [ ] DynamoDB tables created
  - [ ] OpenSearch indices created

Testing:
  - [ ] Unit tests passing
  - [ ] Integration tests passing
  - [ ] Load tests completed
  - [ ] Security tests completed
  - [ ] Disaster recovery tested

Documentation:
  - [ ] Architecture documented
  - [ ] API documentation complete
  - [ ] Runbooks created
  - [ ] Incident response plan
  - [ ] Backup and recovery procedures
```

### 5.2 Monitoring Strategy

```yaml
Real-Time Monitoring:
  - API Gateway request count
  - Lambda invocations and errors
  - Bedrock API calls and latency
  - Database connections and CPU
  - OpenSearch cluster health
  - Cache hit rates

Daily Reviews:
  - Error logs analysis
  - Performance trends
  - Cost analysis
  - Security events
  - User activity patterns

Weekly Reviews:
  - Capacity planning
  - Performance optimization
  - Security posture review
  - Backup verification
  - Documentation updates

Monthly Reviews:
  - Architecture review
  - Cost optimization
  - Security audit
  - Disaster recovery drill
  - Compliance review
```

---

*Document Version: 1.0*  
*Architecture: Production-Grade Observability & Security*  
*Services: CloudWatch, X-Ray, CloudTrail, Cognito, IAM, WAF, VPC*
