# Restore Aurora from Snapshot

$REGION = "ap-south-1"
$SNAPSHOT_ID = "stack1-snapshot-hiveminddb-xq9pxaszsvgp"
$DB_CLUSTER_ID = "hivemind-aurora-cluster"
$DB_INSTANCE_ID = "hivemind-aurora-instance"
$DB_NAME = "hiveminddb"
$DB_USER = "hivemind"
$DB_PASSWORD = "HiveMind2024!Secure"
$DB_SUBNET_GROUP = "hivemind-db-subnet-group"
$SG_ID = "sg-0bb76b17b91d04509"

Write-Host "Restoring Aurora from Snapshot" -ForegroundColor Cyan
Write-Host ""

# Restore cluster
Write-Host "Restoring cluster from snapshot..." -ForegroundColor Yellow
aws rds restore-db-cluster-from-snapshot `
    --db-cluster-identifier $DB_CLUSTER_ID `
    --snapshot-identifier $SNAPSHOT_ID `
    --engine aurora-postgresql `
    --db-subnet-group-name $DB_SUBNET_GROUP `
    --vpc-security-group-ids $SG_ID `
    --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=1 `
    --region $REGION `
    --no-cli-pager

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to restore cluster" -ForegroundColor Red
    exit 1
}

Write-Host "Cluster restore initiated" -ForegroundColor Green

# Wait a bit
Write-Host ""
Write-Host "Waiting 30 seconds..." -ForegroundColor Gray
Start-Sleep -Seconds 30

# Create instance
Write-Host ""
Write-Host "Creating instance..." -ForegroundColor Yellow
aws rds create-db-instance `
    --db-instance-identifier $DB_INSTANCE_ID `
    --db-instance-class db.serverless `
    --engine aurora-postgresql `
    --db-cluster-identifier $DB_CLUSTER_ID `
    --publicly-accessible `
    --region $REGION `
    --no-cli-pager

if ($LASTEXITCODE -eq 0) {
    Write-Host "Instance created" -ForegroundColor Green
}

# Wait for available
Write-Host ""
Write-Host "Waiting for cluster to become available..." -ForegroundColor Yellow
Write-Host "  (Takes ~5 minutes)" -ForegroundColor Gray

aws rds wait db-cluster-available --db-cluster-identifier $DB_CLUSTER_ID --region $REGION

# Get endpoint
$ENDPOINT = aws rds describe-db-clusters `
    --db-cluster-identifier $DB_CLUSTER_ID `
    --query "DBClusters[0].Endpoint" `
    --output text `
    --region $REGION

Write-Host ""
Write-Host "Database Restored!" -ForegroundColor Green
Write-Host ""
Write-Host "Connection Details:" -ForegroundColor Cyan
Write-Host "  Host: $ENDPOINT" -ForegroundColor White
Write-Host "  Port: 5432" -ForegroundColor White
Write-Host "  Database: $DB_NAME" -ForegroundColor White
Write-Host "  User: $DB_USER" -ForegroundColor White
Write-Host ""

# Save config
$config = @"
DB_HOST=$ENDPOINT
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
"@

$config | Out-File -FilePath "db-config.env" -Encoding utf8
Write-Host "Config saved to db-config.env" -ForegroundColor Green
Write-Host ""
Write-Host "Next: .\update-lambda-db-config.ps1" -ForegroundColor Yellow
