# HiveMind Production .gitignore

## Critical Security Rules

### ✅ What IS Committed
- Source code (`.py`, `.ts`, `.tsx`, `.js`)
- Configuration templates (`.env.example`)
- Documentation (`.md`)
- Database schemas (`.sql`)
- CloudFormation templates (`.yaml`)
- Package definitions (`requirements.txt`, `package.json`)

### ❌ What is NOT Committed
- **Secrets**: `.env`, `*.pem`, `*.key`, credentials
- **Dependencies**: `node_modules/`, `venv/`
- **Build artifacts**: `.next/`, `dist/`, `build/`
- **Logs**: `*.log`, `backend.log`, `frontend.log`
- **Databases**: `*.db`, `*.sqlite`
- **Uploads**: `uploads/`, `media/`, `videos/`
- **IDE files**: `.vscode/`, `.idea/`
- **OS files**: `.DS_Store`, `Thumbs.db`

---

## Security Checklist

Before committing:

- [ ] No `.env` files (only `.env.example`)
- [ ] No AWS credentials or keys
- [ ] No database passwords
- [ ] No API keys (NewsAPI, etc.)
- [ ] No PEM files or certificates
- [ ] No `node_modules/` or `venv/`
- [ ] No log files
- [ ] No uploaded media files
- [ ] No database files

---

## Verify Before Push

```bash
# Check for secrets
git diff --cached | grep -i "password\|secret\|key\|token"

# Check for .env files
git status | grep ".env"

# Check file sizes (should be small)
git ls-files -s | awk '{if($4>1000000) print $4}'
```

---

## If You Accidentally Commit Secrets

```bash
# Remove from history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/secret/file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (DANGEROUS - coordinate with team)
git push origin --force --all

# Rotate all exposed credentials immediately
```

---

## Production Deployment

### What to Deploy
- Source code
- `requirements.txt` / `package.json`
- Database schema (`schema.sql`)
- CloudFormation templates

### What NOT to Deploy
- `.env` files (use AWS Secrets Manager)
- Local databases
- Log files
- Development artifacts

---

## Environment Variables

Store in:
- **Development**: `.env` (local, gitignored)
- **Production**: AWS Secrets Manager / Parameter Store
- **CI/CD**: GitHub Secrets / GitLab Variables

Never commit:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `DB_PASSWORD`
- `NEWS_API_KEY`
- Any credentials or tokens

---

## Summary

✅ **Commit**: Code, docs, templates  
❌ **Never commit**: Secrets, dependencies, builds, logs, uploads  
🔒 **Always verify**: Before every commit and push
