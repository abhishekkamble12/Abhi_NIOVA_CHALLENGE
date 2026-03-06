#!/bin/bash
# Pre-Commit Security Check

echo "🔍 Checking for secrets before commit..."

# Check for .env files
if git diff --cached --name-only | grep -q "\.env$"; then
    echo "❌ ERROR: .env file detected in commit"
    echo "   Remove with: git reset HEAD .env"
    exit 1
fi

# Check for common secret patterns
SECRETS=$(git diff --cached | grep -iE "(password|secret|api_key|access_key|private_key|token).*=.*['\"]?[a-zA-Z0-9]{8,}")
if [ ! -z "$SECRETS" ]; then
    echo "❌ ERROR: Potential secrets detected:"
    echo "$SECRETS"
    echo ""
    echo "   Review and remove secrets before committing"
    exit 1
fi

# Check for AWS credentials
if git diff --cached | grep -qE "AKIA[0-9A-Z]{16}"; then
    echo "❌ ERROR: AWS Access Key detected"
    exit 1
fi

# Check for large files
LARGE_FILES=$(git diff --cached --name-only | xargs -I {} du -k {} 2>/dev/null | awk '$1 > 1024 {print $2}')
if [ ! -z "$LARGE_FILES" ]; then
    echo "⚠️  WARNING: Large files detected (>1MB):"
    echo "$LARGE_FILES"
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for node_modules or venv
if git diff --cached --name-only | grep -qE "(node_modules|venv|\.venv)/"; then
    echo "❌ ERROR: Dependencies detected in commit"
    echo "   Check .gitignore"
    exit 1
fi

echo "✅ Security check passed"
exit 0
