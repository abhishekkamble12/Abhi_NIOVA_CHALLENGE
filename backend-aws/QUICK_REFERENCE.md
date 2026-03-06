# Quick Reference - EC2 Deployment

## 🚀 One-Command Deploy

```bash
./deploy.sh
```

## 📝 Manual Steps

```bash
# 1. Setup
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
nano .env

# 3. Test
python start.py
```

## 🔧 Required .env Values

```bash
AWS_REGION=ap-south-1
DB_HOST=<aurora-endpoint>
DB_USER=postgres
DB_PASSWORD=<password>
DB_NAME=hiveminddb
REDIS_HOST=<redis-endpoint>
S3_BUCKET=hivemind-media
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
```

## ✅ Health Check

```bash
python start.py
# Should show: ✅ All services operational
```

## 🐛 Troubleshooting

### Aurora fails
```bash
# Check security group
# Verify DB_HOST endpoint
psql -h $DB_HOST -U $DB_USER -d $DB_NAME
```

### Redis fails
```bash
# Check security group
# Verify REDIS_HOST endpoint
redis-cli -h $REDIS_HOST ping
```

### S3 fails
```bash
# Check IAM role permissions
aws s3 ls s3://$S3_BUCKET --region ap-south-1
```

### Bedrock fails
```bash
# Check IAM role has bedrock:InvokeModel
# Enable model access in Bedrock console
```

## 📊 Service Endpoints

| Service | Endpoint Format |
|---------|----------------|
| Aurora | `*.cluster-*.ap-south-1.rds.amazonaws.com` |
| Redis | `*.0001.aps1.cache.amazonaws.com` |
| S3 | `https://bucket.s3.ap-south-1.amazonaws.com` |
| Bedrock | `https://bedrock-runtime.ap-south-1.amazonaws.com` |
| EventBridge | `https://events.ap-south-1.amazonaws.com` |

## 🔐 IAM Policy

```json
{
  "Statement": [
    {"Action": ["s3:*"], "Resource": "arn:aws:s3:::hivemind-media/*"},
    {"Action": ["bedrock:InvokeModel"], "Resource": "*"},
    {"Action": ["events:PutEvents"], "Resource": "*"}
  ]
}
```

## 📦 Dependencies

- Python 3.11
- asyncpg (Aurora)
- redis (ElastiCache)
- httpx (HTTP client)
- aws-requests-auth (SigV4)
- python-dotenv (config)

## 🎯 Success Criteria

✅ Aurora: SELECT query works  
✅ Redis: PING returns True  
✅ S3: Upload and download work  
✅ Bedrock: Embedding generation works  
✅ EventBridge: Event publishing works  

## 📞 Support

See `EC2_DEPLOYMENT.md` for detailed guide  
See `FIXES_SUMMARY.md` for what was fixed
