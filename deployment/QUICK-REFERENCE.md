# 🚀 HiveMind Database - Quick Reference

## One-Command Setup

```powershell
cd deployment
.\connect-database.ps1
```

**Time**: ~15 minutes | **Cost**: ~$30/month (dev)

---

## 📦 What Gets Deployed

```
Aurora PostgreSQL Serverless v2
├── Cluster: hivemind-aurora-cluster
├── Instance: hivemind-aurora-instance
├── Database: hiveminddb
├── User: hivemind
└── Tables: 8+ (brands, posts, videos, articles, etc.)

Lambda Functions (9)
├── hivemind-social-create-brand
├── hivemind-social-get-brand
├── hivemind-social-list-brands
├── hivemind-social-get-post
├── hivemind-social-generate-content
├── hivemind-feed-personalized
├── hivemind-video-upload-handler
├── hivemind-ai-generate-content
└── hivemind-ai-process-video

Configuration
└── db-config.env (credentials)
```

---

## 🔧 Manual Steps

```powershell
# 1. Deploy database (10 min)
.\deploy-database.ps1

# 2. Setup schema (1 min)
.\setup-database-schema.ps1

# 3. Connect Lambdas (1 min)
.\update-lambda-db-config.ps1

# 4. Verify everything (30 sec)
.\verify-system.ps1
```

---

## 🧪 Testing Commands

### Test Lambda Directly
```powershell
aws lambda invoke --function-name hivemind-social-list-brands --region ap-south-1 response.json
cat response.json
```

### Test API Gateway
```bash
# List brands
curl https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod/social/brands

# Create brand
curl -X POST https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod/social/brands \
  -H "Content-Type: application/json" \
  -d '{"name":"TechCorp","industry":"Technology"}'

# Get specific brand
curl https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod/social/brands/{id}
```

### Test Database Directly
```bash
# Connect
psql -h <DB_HOST> -U hivemind -d hiveminddb

# List tables
\dt

# Query brands
SELECT * FROM brands;

# Check vector extension
SELECT * FROM pg_extension WHERE extname = 'vector';
```

---

## 📊 System Architecture

```
┌──────────────┐
│   Frontend   │  http://hivemind-frontend-83016.s3-website.ap-south-1.amazonaws.com
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ API Gateway  │  https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod
└──────┬───────┘
       │
       ▼
┌──────────────┐      ┌─────────────┐
│   Lambda     │─────▶│   Aurora    │
│ (9 functions)│      │ PostgreSQL  │
└──────┬───────┘      └─────────────┘
       │
       ▼
┌──────────────┐
│      S3      │
│ media-ai-    │
│  content     │
└──────────────┘
```

---

## 🗄️ Database Schema

### Core Tables
- **brands** - Brand profiles (id, name, industry, tone)
- **social_posts** - Posts (id, brand_id, platform, content, status)
- **post_engagement** - Metrics (likes, comments, shares, impressions)
- **articles** - News (id, title, url, category, embedding)
- **videos** - Video metadata (id, s3_url, duration, thumbnail)
- **video_scenes** - Scene detection (id, video_id, start_time, end_time)
- **video_captions** - Transcriptions (id, video_id, text, language)
- **user_preferences** - User settings (id, user_id, keywords, categories)

### Vector Tables (AI Features)
- **user_interest_embeddings** - User preference vectors
- **content_similarity_cache** - Pre-computed similarities
- **cross_module_links** - Content connections across modules

---

## 🔑 Environment Variables

### Lambda Functions
```bash
S3_BUCKET=media-ai-content
DB_HOST=hivemind-aurora-cluster.xxxxx.ap-south-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=hiveminddb
DB_USER=hivemind
DB_PASSWORD=HiveMind2024!Secure
```

### Frontend
```bash
NEXT_PUBLIC_API_URL=https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod
```

---

## 🐛 Quick Troubleshooting

### Lambda can't connect to DB
```powershell
# Check Lambda config
aws lambda get-function-configuration --function-name hivemind-social-list-brands --region ap-south-1

# Check logs
aws logs tail /aws/lambda/hivemind-social-list-brands --follow --region ap-south-1

# Re-update config
.\update-lambda-db-config.ps1
```

### Database connection timeout
```powershell
# Check cluster status
aws rds describe-db-clusters --db-cluster-identifier hivemind-aurora-cluster --region ap-south-1

# Check security group
aws ec2 describe-security-groups --group-names hivemind-db-sg --region ap-south-1
```

### CORS errors on frontend
```powershell
# Rebuild Lambda packages with CORS
.\rebuild-with-cors.ps1
```

---

## 💰 Cost Breakdown

### Aurora Serverless v2
- **Active**: $0.12/hour
- **Idle**: $0/hour (auto-scales to 0)
- **Storage**: $0.10/GB-month
- **Dev (8h/day)**: ~$29/month
- **Prod (24/7)**: ~$86/month

### Lambda
- **Free tier**: 1M requests/month
- **After**: $0.20 per 1M requests
- **Typical**: < $5/month

### S3
- **Storage**: $0.023/GB-month
- **Requests**: Minimal cost
- **Typical**: < $2/month

### API Gateway
- **Free tier**: 1M requests/month
- **After**: $3.50 per 1M requests
- **Typical**: < $5/month

**Total Dev**: ~$35/month
**Total Prod**: ~$100/month

---

## 🔐 Security Checklist

- [ ] Change default database password
- [ ] Disable public access for production
- [ ] Use AWS Secrets Manager for credentials
- [ ] Restrict security group to Lambda only
- [ ] Enable CloudWatch logging
- [ ] Set up backup retention
- [ ] Enable encryption at rest
- [ ] Use IAM roles (not access keys)

---

## 📚 File Reference

| File | Purpose |
|------|---------|
| `connect-database.ps1` | Master script (runs all steps) |
| `deploy-database.ps1` | Deploy Aurora cluster |
| `setup-database-schema.ps1` | Initialize tables |
| `update-lambda-db-config.ps1` | Configure Lambda functions |
| `verify-system.ps1` | Health check all components |
| `rebuild-with-cors.ps1` | Fix CORS issues |
| `db-config.env` | Database credentials (generated) |
| `DATABASE-SETUP.md` | Full documentation |

---

## 🎯 Success Criteria

✅ Aurora cluster status: **available**
✅ Lambda functions: **9 deployed**
✅ Database tables: **8+ created**
✅ API Gateway: **responding**
✅ Frontend: **loading**
✅ CORS: **enabled**
✅ Logs: **no errors**

**Verify**: Run `.\verify-system.ps1`

---

## 🆘 Support

**CloudWatch Logs**:
```powershell
aws logs tail /aws/lambda/hivemind-social-list-brands --follow --region ap-south-1
```

**RDS Events**:
```powershell
aws rds describe-events --source-identifier hivemind-aurora-cluster --region ap-south-1
```

**Database Queries**:
```sql
-- Check connections
SELECT count(*) FROM pg_stat_activity;

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables WHERE schemaname = 'public';
```

---

## 🔄 Cleanup (Delete Everything)

```powershell
# Delete database
aws rds delete-db-instance --db-instance-identifier hivemind-aurora-instance --skip-final-snapshot --region ap-south-1
aws rds delete-db-cluster --db-cluster-identifier hivemind-aurora-cluster --skip-final-snapshot --region ap-south-1

# Delete networking
aws rds delete-db-subnet-group --db-subnet-group-name hivemind-db-subnet-group --region ap-south-1
aws ec2 delete-security-group --group-name hivemind-db-sg --region ap-south-1

# Delete config
rm db-config.env
```

---

**Last Updated**: 2024
**Region**: ap-south-1 (Mumbai)
**Status**: ✅ Production Ready
