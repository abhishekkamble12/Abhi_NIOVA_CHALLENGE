# Verify Database Connection - System Health Check

$REGION = "ap-south-1"
$API_URL = "https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🔍 HiveMind System Health Check" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# Check 1: Database Config File
Write-Host "1. Database Configuration" -ForegroundColor Yellow
Write-Host "   ─────────────────────────" -ForegroundColor Gray
if (Test-Path "db-config.env") {
    $config = @{}
    Get-Content "db-config.env" | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $config[$matches[1]] = $matches[2]
        }
    }
    Write-Host "   ✓ Config file found" -ForegroundColor Green
    Write-Host "     Host: $($config['DB_HOST'])" -ForegroundColor Gray
    Write-Host "     Database: $($config['DB_NAME'])" -ForegroundColor Gray
} else {
    Write-Host "   ✗ Config file missing" -ForegroundColor Red
    $allPassed = $false
}
Write-Host ""

# Check 2: Aurora Cluster Status
Write-Host "2. Aurora Cluster Status" -ForegroundColor Yellow
Write-Host "   ─────────────────────────" -ForegroundColor Gray
$clusterStatus = aws rds describe-db-clusters --db-cluster-identifier hivemind-aurora-cluster --query "DBClusters[0].Status" --output text --region $REGION 2>$null
if ($clusterStatus -eq "available") {
    Write-Host "   ✓ Cluster is available" -ForegroundColor Green
    $endpoint = aws rds describe-db-clusters --db-cluster-identifier hivemind-aurora-cluster --query "DBClusters[0].Endpoint" --output text --region $REGION
    Write-Host "     Endpoint: $endpoint" -ForegroundColor Gray
} else {
    Write-Host "   ✗ Cluster status: $clusterStatus" -ForegroundColor Red
    $allPassed = $false
}
Write-Host ""

# Check 3: Lambda Functions
Write-Host "3. Lambda Functions" -ForegroundColor Yellow
Write-Host "   ─────────────────────────" -ForegroundColor Gray
$functions = aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'hivemind-')].FunctionName" --output text --region $REGION
$functionList = $functions -split '\s+'
Write-Host "   ✓ Found $($functionList.Count) functions" -ForegroundColor Green

# Check if they have DB config
$configuredCount = 0
foreach ($func in $functionList | Select-Object -First 3) {
    $envVars = aws lambda get-function-configuration --function-name $func --query "Environment.Variables.DB_HOST" --output text --region $REGION 2>$null
    if ($envVars -and $envVars -ne "PLACEHOLDER") {
        $configuredCount++
    }
}
if ($configuredCount -gt 0) {
    Write-Host "   ✓ $configuredCount functions have DB config" -ForegroundColor Green
} else {
    Write-Host "   ✗ Functions not configured with database" -ForegroundColor Red
    $allPassed = $false
}
Write-Host ""

# Check 4: Direct Database Connection
Write-Host "4. Direct Database Connection" -ForegroundColor Yellow
Write-Host "   ─────────────────────────" -ForegroundColor Gray
$psqlExists = Get-Command psql -ErrorAction SilentlyContinue
if ($psqlExists -and (Test-Path "db-config.env")) {
    $config = @{}
    Get-Content "db-config.env" | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $config[$matches[1]] = $matches[2]
        }
    }
    
    $env:PGPASSWORD = $config['DB_PASSWORD']
    $testQuery = psql -h $config['DB_HOST'] -U $config['DB_USER'] -d $config['DB_NAME'] -t -c "SELECT COUNT(*) FROM brands;" 2>$null
    $env:PGPASSWORD = $null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Database connection successful" -ForegroundColor Green
        Write-Host "     Brands in database: $($testQuery.Trim())" -ForegroundColor Gray
    } else {
        Write-Host "   ✗ Cannot connect to database" -ForegroundColor Red
        $allPassed = $false
    }
} else {
    Write-Host "   ⚠ psql not installed, skipping direct test" -ForegroundColor Yellow
}
Write-Host ""

# Check 5: Lambda → Database Connection
Write-Host "5. Lambda → Database Connection" -ForegroundColor Yellow
Write-Host "   ─────────────────────────" -ForegroundColor Gray
Write-Host "   Testing hivemind-social-list-brands..." -ForegroundColor Gray

aws lambda invoke --function-name hivemind-social-list-brands --region $REGION response.json --no-cli-pager 2>$null

if (Test-Path response.json) {
    $response = Get-Content response.json -Raw | ConvertFrom-Json
    
    if ($response.statusCode -eq 200) {
        Write-Host "   ✓ Lambda can connect to database" -ForegroundColor Green
        $body = $response.body | ConvertFrom-Json
        Write-Host "     Brands returned: $($body.brands.Count)" -ForegroundColor Gray
    } else {
        Write-Host "   ✗ Lambda returned error: $($response.statusCode)" -ForegroundColor Red
        Write-Host "     $($response.body)" -ForegroundColor Gray
        $allPassed = $false
    }
    Remove-Item response.json
} else {
    Write-Host "   ✗ Lambda invocation failed" -ForegroundColor Red
    $allPassed = $false
}
Write-Host ""

# Check 6: API Gateway → Lambda → Database
Write-Host "6. API Gateway End-to-End" -ForegroundColor Yellow
Write-Host "   ─────────────────────────" -ForegroundColor Gray
Write-Host "   Testing $API_URL/social/brands..." -ForegroundColor Gray

try {
    $apiResponse = Invoke-RestMethod -Uri "$API_URL/social/brands" -Method Get -ErrorAction Stop
    Write-Host "   ✓ API Gateway working" -ForegroundColor Green
    Write-Host "     Brands: $($apiResponse.brands.Count)" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ API Gateway error: $($_.Exception.Message)" -ForegroundColor Red
    $allPassed = $false
}
Write-Host ""

# Check 7: pgvector Extension
Write-Host "7. Vector Database Features" -ForegroundColor Yellow
Write-Host "   ─────────────────────────" -ForegroundColor Gray
if ($psqlExists -and (Test-Path "db-config.env")) {
    $config = @{}
    Get-Content "db-config.env" | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $config[$matches[1]] = $matches[2]
        }
    }
    
    $env:PGPASSWORD = $config['DB_PASSWORD']
    $vectorCheck = psql -h $config['DB_HOST'] -U $config['DB_USER'] -d $config['DB_NAME'] -t -c "SELECT COUNT(*) FROM pg_extension WHERE extname='vector';" 2>$null
    $env:PGPASSWORD = $null
    
    if ($vectorCheck -and $vectorCheck.Trim() -eq "1") {
        Write-Host "   ✓ pgvector extension enabled" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ pgvector not enabled (optional)" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠ Skipped (psql not available)" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "  ✅ All Critical Checks Passed!" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🎉 Your system is fully connected and operational!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  • Create test data via API" -ForegroundColor White
    Write-Host "  • Test frontend at: http://hivemind-frontend-83016.s3-website.ap-south-1.amazonaws.com" -ForegroundColor White
    Write-Host "  • Monitor CloudWatch logs for any issues" -ForegroundColor White
    Write-Host ""
    Write-Host "Quick Test:" -ForegroundColor Yellow
    Write-Host '  curl -X POST $API_URL/social/brands -H "Content-Type: application/json" -d "{\"name\":\"TestBrand\",\"industry\":\"Tech\"}"' -ForegroundColor Gray
} else {
    Write-Host "  ⚠️  Some Checks Failed" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check CloudWatch logs: aws logs tail /aws/lambda/hivemind-social-list-brands --follow" -ForegroundColor Gray
    Write-Host "  2. Verify security group allows port 5432" -ForegroundColor Gray
    Write-Host "  3. Ensure Lambda has DB credentials: aws lambda get-function-configuration --function-name hivemind-social-list-brands" -ForegroundColor Gray
    Write-Host "  4. Review DATABASE-SETUP.md for detailed troubleshooting" -ForegroundColor Gray
}
Write-Host ""
