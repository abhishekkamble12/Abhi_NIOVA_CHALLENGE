# HiveMind AWS Backend - EC2 Deployment Guide

## 🎯 Architecture

Backend running on **EC2 in ap-south-1** connecting to:
- Aurora PostgreSQL (private endpoint in VPC)
- ElastiCache Redis (private endpoint in VPC)
- S3 (regional endpoint via VPC endpoint or internet)
- Bedrock (regional endpoint)
- EventBridge (regional endpoint)

---

## 📋 Prerequisites

1. EC2 instance in ap-south-1 with:
   - Python 3.11
   - Security group allowing outbound HTTPS
   - IAM role with permissions for S3, Bedrock, EventBridge

2. Aurora cluster in same VPC
3. ElastiCache Redis in same VPC
4. S3 bucket in ap-south-1

---

## 🚀 Deployment Steps

### 1. Connect to EC2
```bash
ssh -i your-key.pem ec2-user@your-instance-ip
```

### 2. Install Python 3.11
```bash
sudo yum update -y
sudo yum install python3.11 python3.11-pip git -y
```

### 3. Clone and Setup
```bash
cd /home/ec2-user
git clone <your-repo>
cd aws/backend-aws

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env
```

Required values:
```bash
AWS_REGION=ap-south-1

# Aurora (private endpoint)
DB_HOST=your-cluster.cluster-xxxxx.ap-south-1.rds.amazonaws.com
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=hiveminddb

# Redis (private endpoint)
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

### 5. Test Services
```bash
python start.py
```

Expected output:
```
🚀 HiveMind AWS Backend - Service Health Check
   EC2 Instance in ap-south-1 VPC
======================================================================

🔍 Testing Aurora PostgreSQL...
✅ Aurora connected
   Host: your-cluster.ap-south-1.rds.amazonaws.com
   Database: hiveminddb

🔍 Testing ElastiCache Redis...
✅ Redis connected
   Host: your-cache.aps1.cache.amazonaws.com
   Ping: True

🔍 Testing S3...
✅ S3 upload successful
   Bucket: hivemind-media
   Region: ap-south-1

🔍 Testing Bedrock...
✅ Bedrock embedding generated
   Dimensions: 1536

🔍 Testing EventBridge...
✅ EventBridge event published

📊 Health Check Summary
======================================================================
✅ AURORA: PASS
✅ REDIS: PASS
✅ S3: PASS
✅ BEDROCK: PASS
✅ EVENTBRIDGE: PASS

✅ All services operational - Backend ready!
```

---

## 🔧 Troubleshooting

### Aurora Connection Failed
```bash
# Check security group allows EC2 → Aurora on port 5432
# Verify DB_HOST is the cluster endpoint
# Test with psql:
psql -h $DB_HOST -U $DB_USER -d $DB_NAME
```

### Redis Connection Failed
```bash
# Check security group allows EC2 → Redis on port 6379
# Verify REDIS_HOST is correct
# Test with redis-cli:
redis-cli -h $REDIS_HOST -p 6379 ping
```

### S3 Failed
```bash
# Check IAM role has s3:PutObject, s3:GetObject permissions
# Verify AWS credentials are set
# Test with AWS CLI:
aws s3 ls s3://$S3_BUCKET --region ap-south-1
```

### Bedrock Failed
```bash
# Check IAM role has bedrock:InvokeModel permission
# Verify region is ap-south-1
# Check model access is enabled in Bedrock console
```

### EventBridge Failed
```bash
# Check IAM role has events:PutEvents permission
# Verify EVENT_BUS_NAME exists or use "default"
```

---

## 🔐 IAM Role Permissions

Attach this policy to EC2 IAM role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::hivemind-media/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "events:PutEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 🏃 Running the Backend

### Development
```bash
source venv/bin/activate
python start.py
```

### Production with systemd
```bash
sudo nano /etc/systemd/system/hivemind.service
```

```ini
[Unit]
Description=HiveMind AWS Backend
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/aws/backend-aws
Environment="PATH=/home/ec2-user/aws/backend-aws/venv/bin"
ExecStart=/home/ec2-user/aws/backend-aws/venv/bin/python start.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable hivemind
sudo systemctl start hivemind
sudo systemctl status hivemind
```

---

## 📊 Monitoring

### Check logs
```bash
sudo journalctl -u hivemind -f
```

### Health check endpoint
```bash
curl http://localhost:8000/health
```

---

## ✅ Summary

- ✅ All services use ap-south-1 region
- ✅ Aurora/Redis via private VPC endpoints
- ✅ S3/Bedrock/EventBridge via regional endpoints
- ✅ No boto3/AWS CLI required
- ✅ Direct HTTP/TCP connections
- ✅ Environment variable configuration
- ✅ Comprehensive health checks
