# Update Lambda Functions with Database Config

param(
    [string]$ConfigFile = "db-config.env"
)

$REGION = "ap-south-1"

Write-Host " Updating Lambda Functions with Database Config" -ForegroundColor Cyan
Write-Host ""

# Load config
if (Test-Path $ConfigFile) {
    $config = @{}
    Get-Content $ConfigFile | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $config[$matches[1]] = $matches[2]
        }
    }
    Write-Host " Loaded config from $ConfigFile" -ForegroundColor Green
} else {
    Write-Host " Config file not found: $ConfigFile" -ForegroundColor Red
    Write-Host "Run deploy-database.ps1 first" -ForegroundColor Yellow
    exit 1
}

$DB_HOST = $config['DB_HOST']
$DB_PORT = $config['DB_PORT']
$DB_NAME = $config['DB_NAME']
$DB_USER = $config['DB_USER']
$DB_PASSWORD = $config['DB_PASSWORD']

Write-Host ""
Write-Host "Database Config:" -ForegroundColor Yellow
Write-Host "  Host: $DB_HOST" -ForegroundColor Gray
Write-Host "  Database: $DB_NAME" -ForegroundColor Gray
Write-Host "  User: $DB_USER" -ForegroundColor Gray

# Get all HiveMind Lambda functions
Write-Host ""
Write-Host "Finding Lambda functions..." -ForegroundColor Yellow
$functions = aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'hivemind-')].FunctionName" --output text --region $REGION
$functionList = $functions -split '\s+'

Write-Host "  Found: $($functionList.Count) functions" -ForegroundColor Gray

# Update each function
Write-Host ""
Write-Host "Updating environment variables..." -ForegroundColor Yellow

$updated = 0
foreach ($func in $functionList) {
    Write-Host "  → $func" -ForegroundColor Gray
    
    aws lambda update-function-configuration `
        --function-name $func `
        --environment "Variables={S3_BUCKET=media-ai-content,DB_HOST=$DB_HOST,DB_PORT=$DB_PORT,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD}" `
        --region $REGION `
        --no-cli-pager 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        $updated++
    }
    
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host " Updated $updated/$($functionList.Count) functions" -ForegroundColor Green
Write-Host ""
Write-Host "Test database connection:" -ForegroundColor Yellow
Write-Host "  aws lambda invoke --function-name hivemind-social-list-brands --region ap-south-1 response.json" -ForegroundColor Gray
Write-Host "  cat response.json" -ForegroundColor Gray
