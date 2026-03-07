# 🗄️ Database Deployment Guide

Complete guide to deploy and connect Aurora PostgreSQL to HiveMind Lambda functions.

## 🚀 Quick Start (One Command)

```powershell
cd deployment
.\connect-database.ps1
```

This master script runs all steps automatically:
1. Deploy Aurora PostgreSQL Serverless v2
2. Initialize database schema
3. Update Lambda functions with DB credentials
4. Test connection

**Time Required**: ~15 minutes (mostly waiting for Aurora)

---

## 📋 Manual Step-by-Step

### Step 1: Deploy Aurora Database

```powershell
.\deploy-database.ps1
```

**What it does:**
- Creates Aurora PostgreSQL Serverless v2 cluster
- Configures VPC, subnet group, security group
- Enables public access (for development)
- Saves credentials to `db-config.env`

**Output:**
```
DB_HOST=hivemind-aurora-cluster.xxxxx.ap-south-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=hiveminddb
DB_USER=hivemind
DB_PASSWORD=HiveMind2024!Secure
```

**Cost**: ~$0.12/hour when active, $0 when idle (Serverless v2)

---

### Step 2: Initialize Schema

```powershell
.\setup-database-schema.ps1
```

**What it does:**
- Enables pgvector extension
- Creates base tables (brands, posts, videos, articles)
- Creates vector tables for AI features
- Creates indexes for performance

**Requirements:**
- PostgreSQL client (`psql`) installed
- Install: `choco install postgresql`

**Tables Created:**
- `brands` - Brand profiles
- `social_posts` - Social media posts
- `post_engagement` - Engagement metrics
- `articles` - News articles with embeddings
- `videos` - Video metadata
- `video_scenes` - Scene detection data
- `video_captions` - Transcriptions
- `user_preferences` - User settings

---

### Step 3: Connect Lambda Functions

```powershell
.\update-lambda-db-config.ps1
```

**What it does:**
- Updates all 9 Lambda functions
- Sets DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
- Replaces PLACEHOLDER values

**Functions Updated:**
- hivemind-social-create-brand
- hivemind-social-get-brand
- hivemind-social-list-brands
- hivemind-social-get-post
- hivemind-social-generate-content
- hivemind-feed-personalized
- hivemind-video-upload-handler
- hivemind-ai-generate-content
- hivemind-ai-process-video

---

## 🧪 Testing

### Test Lambda Connection

```powershell
aws lambda invoke --function-name hivemind-social-list-brands --region ap-south-1 response.json
cat response.json
```

### Test API Gateway

```bash
# List brands (should return empty array initially)
curl https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod/social/brands

# Create a brand
curl -X POST https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod/social/brands \
  -H "Content-Type: application/json" \
  -d '{"name":"TechCorp","industry":"Technology"}'
```

### Direct Database Connection

```bash
psql -h <DB_HOST> -U hivemind -d hiveminddb

# List tables
\dt

# Check brands
SELECT * FROM brands;
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│   API Gateway   │
│  wcp5c3ga8b     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Lambda Functions│─────▶│ Aurora PostgreSQL│
│  (9 functions)  │      │  Serverless v2   │
└─────────────────┘      └──────────────────┘
         │                        │
         │                        │
         ▼                        ▼
┌─────────────────┐      ┌──────────────────┐
│   S3 Buckets    │      │   pgvector       │
│ media-ai-content│      │  (embeddings)    │
└─────────────────┘      └──────────────────┘
```

### Database Features

**Base Tables:**
- Brands, posts, videos, articles
- Engagement tracking
- User preferences

**Vector Features (pgvector):**
- Article embeddings (384 dimensions)
- Video scene embeddings
- Semantic search
- Content similarity

**Indexes:**
- IVFFlat indexes for vector search
- B-tree indexes for lookups
- Optimized for < 100K vectors

---

## 🔧 Configuration

### Aurora Serverless v2 Settings

```yaml
Engine: aurora-postgresql 15.4
Scaling:
  Min: 0.5 ACU (~1GB RAM)
  Max: 1 ACU (~2GB RAM)
Network:
  Public: Yes (development)
  Port: 5432
Features:
  - HTTP endpoint enabled
  - pgvector extension
```

### Lambda Environment Variables

```bash
S3_BUCKET=media-ai-content
DB_HOST=<aurora-endpoint>
DB_PORT=5432
DB_NAME=hiveminddb
DB_USER=hivemind
DB_PASSWORD=<secure-password>
```

---

## 🐛 Troubleshooting

### Issue: "psql: command not found"

**Solution:**
```powershell
choco install postgresql
# or download from https://www.postgresql.org/download/windows/
```

### Issue: "Connection timeout"

**Causes:**
1. Security group not allowing port 5432
2. Database not publicly accessible
3. Wrong endpoint

**Solution:**
```powershell
# Check security group
aws ec2 describe-security-groups --group-names hivemind-db-sg --region ap-south-1

# Verify cluster status
aws rds describe-db-clusters --db-cluster-identifier hivemind-aurora-cluster --region ap-south-1
```

### Issue: "Lambda can't connect to database"

**Causes:**
1. Lambda not in same VPC as Aurora
2. Security group blocking Lambda
3. Wrong credentials

**Solution:**
```powershell
# Check Lambda config
aws lambda get-function-configuration --function-name hivemind-social-list-brands --region ap-south-1

# Check CloudWatch logs
aws logs tail /aws/lambda/hivemind-social-list-brands --follow --region ap-south-1
```

### Issue: "pgvector extension not available"

**Solution:**
Aurora PostgreSQL 15.4+ includes pgvector by default. If missing:
```sql
CREATE EXTENSION vector;
```

If error persists, pgvector features will be disabled (non-critical).

---

## 💰 Cost Estimation

### Aurora Serverless v2

**Development (8 hours/day):**
- Active: 8 hours × $0.12/hour = $0.96/day
- Idle: 16 hours × $0/hour = $0
- **Monthly**: ~$29

**Production (24/7):**
- Active: 24 hours × $0.12/hour = $2.88/day
- **Monthly**: ~$86

**Storage:**
- $0.10/GB-month
- Typical: 1-5GB = $0.10-$0.50/month

**Total Development**: ~$30/month
**Total Production**: ~$90/month

### Optimization Tips

1. **Auto-pause**: Enable for dev environments
2. **Scaling**: Keep max at 1 ACU for MVP
3. **Backups**: Use default 1-day retention
4. **Monitoring**: Use CloudWatch (included)

---

## 🔐 Security Best Practices

### For Production

1. **Change default password**:
```powershell
aws rds modify-db-cluster --db-cluster-identifier hivemind-aurora-cluster --master-user-password "NewSecurePassword123!" --region ap-south-1
```

2. **Disable public access**:
```powershell
aws rds modify-db-instance --db-instance-identifier hivemind-aurora-instance --no-publicly-accessible --region ap-south-1
```

3. **Use Secrets Manager**:
```powershell
# Store password
aws secretsmanager create-secret --name hivemind/db/password --secret-string "password" --region ap-south-1

# Update Lambda to use secret
# (requires code changes to fetch from Secrets Manager)
```

4. **Restrict security group**:
```powershell
# Remove 0.0.0.0/0, add Lambda security group only
aws ec2 authorize-security-group-ingress --group-id <sg-id> --source-group <lambda-sg-id> --protocol tcp --port 5432
```

---

## 📊 Monitoring

### CloudWatch Metrics

```powershell
# Database connections
aws cloudwatch get-metric-statistics --namespace AWS/RDS --metric-name DatabaseConnections --dimensions Name=DBClusterIdentifier,Value=hivemind-aurora-cluster --start-time 2024-01-01T00:00:00Z --end-time 2024-01-02T00:00:00Z --period 3600 --statistics Average --region ap-south-1

# CPU utilization
aws cloudwatch get-metric-statistics --namespace AWS/RDS --metric-name CPUUtilization --dimensions Name=DBClusterIdentifier,Value=hivemind-aurora-cluster --start-time 2024-01-01T00:00:00Z --end-time 2024-01-02T00:00:00Z --period 3600 --statistics Average --region ap-south-1
```

### Query Performance

```sql
-- Enable pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- View slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

## 🔄 Cleanup

### Delete Everything

```powershell
# Delete database instance
aws rds delete-db-instance --db-instance-identifier hivemind-aurora-instance --skip-final-snapshot --region ap-south-1

# Delete cluster
aws rds delete-db-cluster --db-cluster-identifier hivemind-aurora-cluster --skip-final-snapshot --region ap-south-1

# Delete subnet group
aws rds delete-db-subnet-group --db-subnet-group-name hivemind-db-subnet-group --region ap-south-1

# Delete security group
aws ec2 delete-security-group --group-name hivemind-db-sg --region ap-south-1
```

---

## 📚 Additional Resources

- [Aurora Serverless v2 Docs](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Lambda + RDS Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/services-rds.html)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

## ✅ Checklist

- [ ] Aurora cluster deployed
- [ ] Database schema initialized
- [ ] Lambda functions updated
- [ ] Connection tested successfully
- [ ] API Gateway working
- [ ] Frontend can fetch data
- [ ] CloudWatch logs show no errors
- [ ] Security group configured
- [ ] Credentials stored securely
- [ ] Monitoring enabled

---

**Need Help?**
- Check CloudWatch logs: `/aws/lambda/hivemind-*`
- Review RDS events in AWS Console
- Test direct psql connection first
- Verify security group rules
