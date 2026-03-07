# Deploy Aurora PostgreSQL Database

$REGION = "ap-south-1"
$DB_CLUSTER_ID = "hivemind-aurora-cluster"
$DB_INSTANCE_ID = "hivemind-aurora-instance"
$DB_NAME = "hiveminddb"
$DB_USER = "hivemind"
$DB_PASSWORD = "HiveMind2024!Secure"
$DB_SUBNET_GROUP = "hivemind-db-subnet-group"
$DB_SECURITY_GROUP = "hivemind-db-sg"
$VPC_ID = ""

Write-Host "Deploying Aurora PostgreSQL Database" -ForegroundColor Cyan
Write-Host ""

# Get default VPC
Write-Host "Getting VPC..." -ForegroundColor Yellow
$VPC_ID = aws ec2 describe-vpcs --filters Name=is-default,Values=true --query "Vpcs[0].VpcId" --output text --region $REGION
Write-Host "VPC: $VPC_ID" -ForegroundColor Gray

# Get subnets
Write-Host "Getting subnets..." -ForegroundColor Yellow
$SUBNETS = aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC_ID --query "Subnets[*].SubnetId" --output text --region $REGION
$SUBNET_LIST = $SUBNETS -split '\s+'
Write-Host "Subnets found: $($SUBNET_LIST.Count)" -ForegroundColor Gray

# Create DB subnet group
Write-Host ""
Write-Host "Creating DB subnet group..." -ForegroundColor Yellow

aws rds create-db-subnet-group `
--db-subnet-group-name $DB_SUBNET_GROUP `
--db-subnet-group-description "HiveMind Aurora subnet group" `
--subnet-ids $SUBNET_LIST `
--region $REGION 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Created subnet group" -ForegroundColor Green
} else {
    Write-Host "Subnet group already exists" -ForegroundColor Gray
}

# Create security group
Write-Host ""
Write-Host "Creating security group..." -ForegroundColor Yellow

$SG_ID = aws ec2 create-security-group `
--group-name $DB_SECURITY_GROUP `
--description "HiveMind Aurora security group" `
--vpc-id $VPC_ID `
--query GroupId `
--output text `
--region $REGION 2>$null

if ($LASTEXITCODE -eq 0) {

    Write-Host "Security group created: $SG_ID" -ForegroundColor Green

    aws ec2 authorize-security-group-ingress `
    --group-id $SG_ID `
    --protocol tcp `
    --port 5432 `
    --cidr 0.0.0.0/0 `
    --region $REGION 2>$null

    Write-Host "Port 5432 opened" -ForegroundColor Green

} else {

    $SG_ID = aws ec2 describe-security-groups `
    --filters Name=group-name,Values=$DB_SECURITY_GROUP `
    --query "SecurityGroups[0].GroupId" `
    --output text `
    --region $REGION

    Write-Host "Security group already exists: $SG_ID" -ForegroundColor Gray
}

# Check if cluster already exists
Write-Host ""
Write-Host "Checking for existing cluster..." -ForegroundColor Yellow
$existingCluster = aws rds describe-db-clusters --db-cluster-identifier $DB_CLUSTER_ID --region $REGION 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Cluster already exists!" -ForegroundColor Green
    $clusterStatus = aws rds describe-db-clusters --db-cluster-identifier $DB_CLUSTER_ID --query "DBClusters[0].Status" --output text --region $REGION
    Write-Host "  Status: $clusterStatus" -ForegroundColor Gray
    
    if ($clusterStatus -ne "available") {
        Write-Host "  Waiting for cluster to become available..." -ForegroundColor Yellow
        aws rds wait db-cluster-available --db-cluster-identifier $DB_CLUSTER_ID --region $REGION 2>$null
    }
} else {
    # Create Aurora cluster
    Write-Host "Creating Aurora PostgreSQL cluster..." -ForegroundColor Yellow
    Write-Host "  (This takes 5-10 minutes)" -ForegroundColor Gray
    
    aws rds create-db-cluster `
        --db-cluster-identifier $DB_CLUSTER_ID `
        --engine aurora-postgresql `
        --engine-version 15.4 `
        --master-username $DB_USER `
        --master-user-password $DB_PASSWORD `
        --database-name $DB_NAME `
        --db-subnet-group-name $DB_SUBNET_GROUP `
        --vpc-security-group-ids $SG_ID `
        --enable-http-endpoint `
        --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=1 `
        --region $REGION `
        --no-cli-pager
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create cluster" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✓ Cluster created" -ForegroundColor Green
    
    # Create Aurora instance
    Write-Host ""
    Write-Host "Creating Aurora instance..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    aws rds create-db-instance `
        --db-instance-identifier $DB_INSTANCE_ID `
        --db-instance-class db.serverless `
        --engine aurora-postgresql `
        --db-cluster-identifier $DB_CLUSTER_ID `
        --publicly-accessible `
        --region $REGION `
        --no-cli-pager
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Instance created" -ForegroundColor Green
    }
}

# Wait for cluster
Write-Host ""
Write-Host "Waiting for cluster to become available..." -ForegroundColor Yellow
Write-Host "  (Grab coffee ☕ - takes ~10 minutes)" -ForegroundColor Gray

aws rds wait db-cluster-available --db-cluster-identifier $DB_CLUSTER_ID --region $REGION 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Cluster is available!" -ForegroundColor Green
} else {
    Write-Host "⚠ Timeout waiting for cluster" -ForegroundColor Yellow
    Write-Host "  Check AWS Console for status" -ForegroundColor Gray
}

# Get endpoint
$ENDPOINT = aws rds describe-db-clusters `
    --db-cluster-identifier $DB_CLUSTER_ID `
    --query "DBClusters[0].Endpoint" `
    --output text `
    --region $REGION 2>$null

if (-not $ENDPOINT -or $ENDPOINT -eq "None") {
    Write-Host ""
    Write-Host "⚠ Could not get endpoint" -ForegroundColor Yellow
    Write-Host "  Run: .\check-database.ps1" -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "✅ Database Deployed!" -ForegroundColor Green
Write-Host ""
Write-Host "Connection Details:" -ForegroundColor Cyan
Write-Host "  Host: $ENDPOINT" -ForegroundColor White
Write-Host "  Port: 5432" -ForegroundColor White
Write-Host "  Database: $DB_NAME" -ForegroundColor White
Write-Host "  User: $DB_USER" -ForegroundColor White
Write-Host "  Password: $DB_PASSWORD" -ForegroundColor White

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Run: .\setup-database-schema.ps1" -ForegroundColor Gray
Write-Host "  2. Run: .\update-lambda-db-config.ps1" -ForegroundColor Gray
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
Write-Host "💾 Config saved to db-config.env" -ForegroundColor Green