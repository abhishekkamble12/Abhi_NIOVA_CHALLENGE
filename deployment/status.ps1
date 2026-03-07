# Quick Database Status Check

$REGION = "ap-south-1"

Write-Host " Checking AWS RDS Status" -ForegroundColor Cyan
Write-Host ""

# Check clusters
Write-Host "Aurora Clusters:" -ForegroundColor Yellow
aws rds describe-db-clusters --query "DBClusters[*].[DBClusterIdentifier,Status,Endpoint]" --output table --region $REGION

Write-Host ""
Write-Host "DB Instances:" -ForegroundColor Yellow
aws rds describe-db-instances --query "DBInstances[*].[DBInstanceIdentifier,DBInstanceStatus,Endpoint.Address]" --output table --region $REGION

Write-Host ""
Write-Host "Snapshots:" -ForegroundColor Yellow
aws rds describe-db-cluster-snapshots --query "DBClusterSnapshots[*].[DBClusterSnapshotIdentifier,Status,SnapshotCreateTime]" --output table --region $REGION

Write-Host ""
Write-Host "Subnet Groups:" -ForegroundColor Yellow
aws rds describe-db-subnet-groups --query "DBSubnetGroups[*].DBSubnetGroupName" --output table --region $REGION

Write-Host ""
Write-Host "Security Groups:" -ForegroundColor Yellow
aws ec2 describe-security-groups --filters "Name=group-name,Values=hivemind-db-sg" --query "SecurityGroups[*].[GroupId,GroupName]" --output table --region $REGION
