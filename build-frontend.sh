#!/bin/bash
set -e

# HiveMind Frontend Build & Deployment Script
# Builds Next.js and deploys to S3 + CloudFront

S3_BUCKET="${S3_FRONTEND_BUCKET}"
API_URL="${NEXT_PUBLIC_API_URL}"
REGION="${AWS_REGION:-ap-south-1}"
CLOUDFRONT_ID="${CLOUDFRONT_DISTRIBUTION_ID}"

echo "🚀 HiveMind Frontend Build & Deployment"
echo "========================================"

# Validate parameters
if [ -z "$S3_BUCKET" ]; then
    echo "❌ Error: S3_FRONTEND_BUCKET not set"
    echo "Usage: S3_FRONTEND_BUCKET=your-bucket NEXT_PUBLIC_API_URL=https://api.example.com ./build-frontend.sh"
    exit 1
fi

if [ -z "$API_URL" ]; then
    echo "⚠️  Warning: NEXT_PUBLIC_API_URL not set, using placeholder"
    API_URL="https://api-placeholder.execute-api.ap-south-1.amazonaws.com/prod"
fi

# Step 1: Set environment variables
echo ""
echo "📝 Configuring environment..."
echo "NEXT_PUBLIC_API_URL=$API_URL" > .env.production
echo "  ✅ Created .env.production"

# Step 2: Install dependencies
echo ""
echo "📦 Installing dependencies..."
npm install --silent
echo "  ✅ Dependencies installed"

# Step 3: Build Next.js
echo ""
echo "🔨 Building Next.js application..."
npm run build
echo "  ✅ Build complete"

# Step 4: Verify output directory
if [ ! -d "out" ]; then
    echo "❌ Error: out/ directory not found"
    exit 1
fi

FILE_COUNT=$(find out -type f | wc -l)
echo "  📄 Generated $FILE_COUNT files"

# Step 5: Upload to S3
echo ""
echo "☁️  Uploading to S3..."

# Sync files to S3
aws s3 sync out/ s3://$S3_BUCKET/ \
    --delete \
    --cache-control "public, max-age=31536000, immutable" \
    --exclude "*.html" \
    --region $REGION

# Upload HTML files with different cache settings
aws s3 sync out/ s3://$S3_BUCKET/ \
    --exclude "*" \
    --include "*.html" \
    --cache-control "public, max-age=0, must-revalidate" \
    --region $REGION

echo "  ✅ Files uploaded to s3://$S3_BUCKET/"

# Step 6: Set bucket website configuration
echo ""
echo "🌐 Configuring S3 website hosting..."

cat > website-config.json <<EOF
{
    "IndexDocument": {
        "Suffix": "index.html"
    },
    "ErrorDocument": {
        "Key": "404.html"
    }
}
EOF

aws s3api put-bucket-website \
    --bucket $S3_BUCKET \
    --website-configuration file://website-config.json \
    --region $REGION

rm website-config.json
echo "  ✅ Website hosting configured"

# Step 7: Invalidate CloudFront (if distribution ID provided)
if [ -n "$CLOUDFRONT_ID" ]; then
    echo ""
    echo "🔄 Invalidating CloudFront cache..."
    
    INVALIDATION_ID=$(aws cloudfront create-invalidation \
        --distribution-id $CLOUDFRONT_ID \
        --paths "/*" \
        --query 'Invalidation.Id' \
        --output text)
    
    echo "  ✅ Invalidation created: $INVALIDATION_ID"
else
    echo ""
    echo "⚠️  Skipping CloudFront invalidation (no distribution ID)"
fi

# Step 8: Get website URL
echo ""
echo "📊 Deployment Summary"
echo "====================="

WEBSITE_URL="http://$S3_BUCKET.s3-website.$REGION.amazonaws.com"
echo "S3 Website URL: $WEBSITE_URL"

if [ -n "$CLOUDFRONT_ID" ]; then
    CF_DOMAIN=$(aws cloudfront get-distribution \
        --id $CLOUDFRONT_ID \
        --query 'Distribution.DomainName' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$CF_DOMAIN" ]; then
        echo "CloudFront URL: https://$CF_DOMAIN"
    fi
fi

echo ""
echo "API Endpoint: $API_URL"
echo "Files Deployed: $FILE_COUNT"

echo ""
echo "✅ Deployment Complete!"
