# HiveMind Backend - Fixed for EC2 in ap-south-1

## 🔧 What Was Fixed

### 1. **Region Configuration**
- ✅ Changed all services to use `ap-south-1`
- ✅ Fixed Redis endpoint from `use1` to `aps1`
- ✅ Updated all AWS service endpoints to ap-south-1

### 2. **Environment Variables**
- ✅ Standardized to: `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- ✅ Standardized to: `REDIS_HOST`, `REDIS_PORT`
- ✅ Removed redundant `AURORA_ENDPOINT` → `DB_HOST`
- ✅ Added proper `.env` loading with `python-dotenv`

### 3. **Service Fixes**

**Aurora Service**
- ✅ Uses `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- ✅ Direct asyncpg connection string
- ✅ Proper transaction management

**Redis Service**
- ✅ Uses `REDIS_HOST` instead of `REDIS_ENDPOINT`
- ✅ Added `ping()` method for health checks
- ✅ Fixed SSL configuration (false for VPC)

**S3 Service**
- ✅ Fixed URL construction (no more URL object errors)
- ✅ Uses regional endpoint: `s3.ap-south-1.amazonaws.com`
- ✅ Added timeout handling
- ✅ Proper error handling in `head_file()`

**Bedrock Service**
- ✅ Dynamic endpoint: `bedrock-runtime.ap-south-1.amazonaws.com`
- ✅ Fixed URL construction
- ✅ Added proper timeouts

**EventBridge Service**
- ✅ Dynamic endpoint: `events.ap-south-1.amazonaws.com`
- ✅ Fixed URL construction
- ✅ Uses `default` event bus by default

### 4. **Health Check Script**
- ✅ Comprehensive testing for all services
- ✅ Detailed output with connection info
- ✅ Exit code 0 on success, 1 on failure
- ✅ Tests: Aurora, Redis, S3 upload/download, Bedrock embedding/text, EventBridge

### 5. **Configuration Management**
- ✅ Single `.env` file for all config
- ✅ Proper loading with `python-dotenv`
- ✅ Type-safe settings with Pydantic
- ✅ Cached settings with `@lru_cache()`

---

## 📁 Files Modified

```
backend-aws/
├── .env.example              ✅ Fixed (standardized vars)
├── config/aws_config.py      ✅ Fixed (proper env loading)
├── services/
│   ├── aurora_service.py     ✅ Fixed (DB_HOST, DB_USER)
│   ├── cache_service.py      ✅ Fixed (REDIS_HOST, ping())
│   ├── s3_service.py         ✅ Fixed (URL handling, region)
│   ├── bedrock_service.py    ✅ Fixed (URL handling, region)
│   └── event_service.py      ✅ Fixed (URL handling, region)
├── start.py                  ✅ Fixed (comprehensive tests)
├── deploy.sh                 ✅ New (EC2 deployment script)
└── EC2_DEPLOYMENT.md         ✅ New (deployment guide)
```

---

## 🚀 Quick Start on EC2

```bash
# 1. Upload to EC2
scp -r backend-aws ec2-user@your-instance:/home/ec2-user/

# 2. SSH to EC2
ssh ec2-user@your-instance

# 3. Configure
cd backend-aws
cp .env.example .env
nano .env  # Edit with your values

# 4. Deploy
chmod +x deploy.sh
./deploy.sh
```

---

## ✅ Environment Variables Required

```bash
# Region
AWS_REGION=ap-south-1

# Aurora (private endpoint in VPC)
DB_HOST=your-cluster.cluster-xxxxx.ap-south-1.rds.amazonaws.com
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=hiveminddb

# Redis (private endpoint in VPC)
REDIS_HOST=your-cache.xxxxx.0001.aps1.cache.amazonaws.com
REDIS_PORT=6379
REDIS_SSL=false

# S3
S3_BUCKET=hivemind-media
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# Bedrock
BEDROCK_MODEL_EMBEDDING=amazon.titan-embed-text-v2:0
BEDROCK_MODEL_TEXT=anthropic.claude-3-sonnet-20240229-v1:0

# EventBridge
EVENT_BUS_NAME=default
```

---

## 🧪 Testing

```bash
python start.py
```

Expected output:
```
✅ AURORA: PASS
✅ REDIS: PASS
✅ S3: PASS
✅ BEDROCK: PASS
✅ EVENTBRIDGE: PASS

✅ All services operational - Backend ready!
```

---

## 🔐 IAM Permissions

EC2 instance needs IAM role with:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::hivemind-media/*"
    },
    {
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel"],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": ["events:PutEvents"],
      "Resource": "*"
    }
  ]
}
```

---

## 🎯 Key Improvements

1. **No more URL decode errors** - Fixed all URL handling
2. **Correct region** - Everything uses ap-south-1
3. **Standardized env vars** - DB_HOST, REDIS_HOST, etc.
4. **VPC-aware** - Redis SSL=false for private endpoints
5. **Comprehensive tests** - All services validated
6. **Production-ready** - Proper error handling, timeouts
7. **Easy deployment** - Single script setup

---

## 📊 Architecture

```
EC2 (ap-south-1)
    ↓
    ├─→ Aurora (private VPC endpoint)
    ├─→ Redis (private VPC endpoint)
    ├─→ S3 (regional endpoint)
    ├─→ Bedrock (regional endpoint)
    └─→ EventBridge (regional endpoint)
```

All services properly configured for EC2 deployment in ap-south-1 VPC! 🎉
