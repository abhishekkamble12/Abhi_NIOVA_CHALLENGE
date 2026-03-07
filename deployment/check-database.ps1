# Check Database Status and Restore if Needed

$REGION = "ap-south-1"
$SNAPSHOT_ID = "stack1-snapshot-hiveminddb-xq9pxaszsvgp"
$DB_CLUSTER_ID = "hivemind-aurora-cluster"
$DB_INSTANCE_ID = "hivemind-aurora-instance"
$DB_NAME = "hiveminddb"
$DB_USER = "hivemind"
$DB_PASSWORD = "HiveMind2024!Secure"
$DB_SUBNET_GROUP = "hivemind-db-subnet-group"
$DB_SECURITY_GROUP = "hivemind-db-sg"

Write-Host "🔍 Checking Database Status" -ForegroundColor Cyan
Write-Host ""

# Check if cluster exists
Write-Host "Checking for existing cluster..." -ForegroundColor Yellow
$existingCluster = aws rds describe-db-clusters --db-cluster-identifier $DB_CLUSTER_ID --region $REGION 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Cluster exists!" -ForegroundColor Green
    $status = aws rds describe-db-clusters --db-cluster-identifier $DB_CLUSTER_ID --query "DBClusters[0].Status" --output text --region $REGION
    $endpoint = aws rds describe-db-clusters --db-cluster-identifier $DB_CLUSTER_ID --query "DBClusters[0].Endpoint" --output text --region $REGION
    
    Write-Host "  Status: $status" -ForegroundColor Gray
    Write-Host "  Endpoint: $endpoint" -ForegroundColor Gray
    
    # Save config
    $config = @"
DB_HOST=$endpoint
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
"@
    $config | Out-File -FilePath "db-config.env" -Encoding utf8
    Write-Host ""
    Write-Host "✅ Database ready! Config saved to db-config.env" -ForegroundColor Green
    exit 0
}

# Check for snapshot
Write-Host "❌ Cluster not found" -ForegroundColor Red
Write-Host ""
Write-Host "Checking for snapshot..." -ForegroundColor Yellow
$snapshot = aws rds describe-db-cluster-snapshots --db-cluster-snapshot-identifier $SNAPSHOT_ID --region $REGION 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Found snapshot: $SNAPSHOT_ID" -ForegroundColor Green
    Write-Host ""
    Write-Host "Would you like to restore from snapshot? (y/n)" -ForegroundColor Yellow
    $restore = Read-Host
    
    if ($restore -eq 'y') {
        Write-Host ""
        Write-Host "Restoring cluster from snapshot..." -ForegroundColor Yellow
        
        # Get security group
        $SG_ID = aws ec2 describe-security-groups --filters Name=group-name,Values=$DB_SECURITY_GROUP --query "SecurityGroups[0].GroupId" --output text --region $REGION
        
        aws rds restore-db-cluster-from-snapshot `
            --db-cluster-identifier $DB_CLUSTER_ID `
            --snapshot-identifier $SNAPSHOT_ID `
            --engine aurora-postgresql `
            --db-subnet-group-name $DB_SUBNET_GROUP `
            --vpc-security-group-ids $SG_ID `
            --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=1 `
            --region $REGION `
            --no-cli-pager
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Cluster restore initiated" -ForegroundColor Green
            
            # Create instance
            Write-Host ""
            Write-Host "Creating instance..." -ForegroundColor Yellow
            Start-Sleep -Seconds 30
            
            aws rds create-db-instance `
                --db-instance-identifier $DB_INSTANCE_ID `
                --db-instance-class db.serverless `
                --engine aurora-postgresql `
                --db-cluster-identifier $DB_CLUSTER_ID `
                --publicly-accessible `
                --region $REGION `
                --no-cli-pager 2>$null
            
            # Wait for available
            Write-Host ""
            Write-Host "Waiting for cluster..." -ForegroundColor Yellow
            aws rds wait db-cluster-available --db-cluster-identifier $DB_CLUSTER_ID --region $REGION
            
            $endpoint = aws rds describe-db-clusters --db-cluster-identifier $DB_CLUSTER_ID --query "DBClusters[0].Endpoint" --output text --region $REGION
            
            Write-Host ""
            Write-Host "✅ Restored from snapshot!" -ForegroundColor Green
            Write-Host "  Endpoint: $endpoint" -ForegroundColor Gray
            
            # Save config
            $config = @"
DB_HOST=$endpoint
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
"@
            $config | Out-File -FilePath "db-config.env" -Encoding utf8
            Write-Host ""
            Write-Host "Config saved to db-config.env" -ForegroundColor Green
        }
    }
} else {
    Write-Host "❌ No snapshot found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Run deploy-database.ps1 to create new cluster" -ForegroundColor Yellow
}
