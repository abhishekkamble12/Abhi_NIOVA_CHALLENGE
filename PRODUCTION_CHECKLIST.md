# 🚀 Production Deployment Checklist

## Pre-Deployment

### Security
- [ ] All `.env` files are gitignored
- [ ] No hardcoded credentials in code
- [ ] AWS credentials stored in Secrets Manager
- [ ] Database passwords rotated
- [ ] API keys secured
- [ ] SSL/TLS certificates configured
- [ ] CORS properly configured (not `allow_origins=["*"]`)
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints

### Code Quality
- [ ] All tests passing
- [ ] No console.log or print statements
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Code reviewed
- [ ] Dependencies updated
- [ ] No unused imports

### Infrastructure
- [ ] Aurora cluster configured
- [ ] ElastiCache Redis configured
- [ ] S3 bucket created with versioning
- [ ] Bedrock models enabled
- [ ] EventBridge bus created
- [ ] VPC and security groups configured
- [ ] IAM roles and policies created
- [ ] CloudWatch alarms configured

### Database
- [ ] Schema deployed (`schema.sql`)
- [ ] Indexes created
- [ ] pgvector extension enabled
- [ ] Backup strategy configured
- [ ] Connection pooling configured

### Configuration
- [ ] Environment variables set in production
- [ ] API endpoints updated
- [ ] CORS origins whitelisted
- [ ] Timeouts configured
- [ ] Cache TTLs optimized

---

## Deployment Steps

### 1. Backend Deployment

```bash
# Connect to EC2
ssh -i your-key.pem ec2-user@your-instance

# Clone repository
git clone <repo-url>
cd aws/backend-aws

# Setup environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Add production values

# Test
python start.py

# Setup systemd service
sudo cp hivemind.service /etc/systemd/system/
sudo systemctl enable hivemind
sudo systemctl start hivemind
```

### 2. Frontend Deployment

```bash
# Build
cd aws
npm install
npm run build

# Deploy to Vercel/Netlify or serve with nginx
npm start
```

### 3. Database Setup

```bash
# Connect to Aurora
psql -h $DB_HOST -U $DB_USER -d $DB_NAME

# Run schema
\i schema.sql

# Verify
\dt
\q
```

---

## Post-Deployment

### Verification
- [ ] Health check endpoint returns 200
- [ ] Can create brand
- [ ] Can generate content
- [ ] Can search news
- [ ] Can upload video
- [ ] Database queries work
- [ ] Redis caching works
- [ ] S3 uploads work
- [ ] Bedrock API works
- [ ] EventBridge events publish

### Monitoring
- [ ] CloudWatch logs configured
- [ ] Alarms set up
- [ ] Error tracking enabled
- [ ] Performance monitoring active
- [ ] Cost alerts configured

### Documentation
- [ ] API documentation updated
- [ ] Deployment guide updated
- [ ] Runbook created
- [ ] Team notified

---

## Production Environment Variables

```bash
# AWS
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=<from-secrets-manager>
AWS_SECRET_ACCESS_KEY=<from-secrets-manager>

# Database
DB_HOST=<aurora-endpoint>
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=<from-secrets-manager>
DB_NAME=hiveminddb

# Redis
REDIS_HOST=<elasticache-endpoint>
REDIS_PORT=6379
REDIS_SSL=false

# S3
S3_BUCKET=hivemind-media-prod

# Bedrock
BEDROCK_MODEL_EMBEDDING=amazon.titan-embed-text-v2:0
BEDROCK_MODEL_TEXT=anthropic.claude-3-sonnet-20240229-v1:0

# News API
NEWS_API_KEY=<from-secrets-manager>

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

---

## Rollback Plan

### If Deployment Fails

```bash
# 1. Stop new service
sudo systemctl stop hivemind

# 2. Restore previous version
git checkout <previous-commit>

# 3. Restart
sudo systemctl start hivemind

# 4. Verify
curl http://localhost:8000/health
```

### Database Rollback

```bash
# Restore from backup
aws rds restore-db-cluster-to-point-in-time \
  --source-db-cluster-identifier hivemind-cluster \
  --db-cluster-identifier hivemind-cluster-restored \
  --restore-to-time 2024-01-15T12:00:00Z
```

---

## Monitoring URLs

- **Application**: https://your-domain.com
- **API**: https://api.your-domain.com
- **Health**: https://api.your-domain.com/health
- **Docs**: https://api.your-domain.com/docs
- **CloudWatch**: AWS Console → CloudWatch
- **Logs**: AWS Console → CloudWatch Logs

---

## Emergency Contacts

- **DevOps Lead**: [contact]
- **Backend Lead**: [contact]
- **AWS Support**: [support-plan]
- **On-Call**: [pagerduty/opsgenie]

---

## Common Issues

### Backend won't start
```bash
# Check logs
sudo journalctl -u hivemind -f

# Check environment
cat .env

# Check dependencies
pip list
```

### Database connection fails
```bash
# Test connection
psql -h $DB_HOST -U $DB_USER -d $DB_NAME

# Check security group
aws ec2 describe-security-groups --group-ids sg-xxxxx
```

### High latency
```bash
# Check CloudWatch metrics
# Check Redis cache hit rate
# Check database query performance
# Check Bedrock API latency
```

---

## Success Criteria

- [ ] All health checks passing
- [ ] Response time < 500ms (p95)
- [ ] Error rate < 1%
- [ ] Uptime > 99.9%
- [ ] All features working
- [ ] No security vulnerabilities
- [ ] Monitoring active
- [ ] Team trained

---

## Sign-Off

- [ ] Backend Lead: _______________
- [ ] Frontend Lead: _______________
- [ ] DevOps Lead: _______________
- [ ] Product Owner: _______________

**Deployment Date**: _______________  
**Deployed By**: _______________  
**Version**: _______________
