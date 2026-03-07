# Deploy Step Functions State Machine

$REGION = "ap-south-1"
$ACCOUNT_ID = "586098609294"

Write-Host "⚙️  Creating Step Functions State Machine..." -ForegroundColor Cyan

# Create IAM role for Step Functions
$sfnTrustPolicy = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "states.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
"@

Set-Content -Path "sfn-trust-policy.json" -Value $sfnTrustPolicy

aws iam create-role `
    --role-name hivemind-stepfunctions-role `
    --assume-role-policy-document file://sfn-trust-policy.json 2>$null

# Create policy for Lambda invocation
$sfnPolicy = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": "arn:aws:lambda:ap-south-1:586098609294:function:hivemind-stepfunctions-*"
    }
  ]
}
"@

Set-Content -Path "sfn-policy.json" -Value $sfnPolicy

aws iam put-role-policy `
    --role-name hivemind-stepfunctions-role `
    --policy-name StepFunctionsLambdaInvoke `
    --policy-document file://sfn-policy.json

$SFN_ROLE_ARN = aws iam get-role `
    --role-name hivemind-stepfunctions-role `
    --query 'Role.Arn' `
    --output text

Write-Host "✅ Step Functions role created: $SFN_ROLE_ARN" -ForegroundColor Green

# Wait for IAM propagation
Write-Host "⏳ Waiting 10 seconds for IAM propagation..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Create state machine
$STATE_MACHINE_ARN = aws stepfunctions create-state-machine `
    --name hivemind-video-processing `
    --definition file://video-processing-state-machine.json `
    --role-arn $SFN_ROLE_ARN `
    --region $REGION `
    --query 'stateMachineArn' `
    --output text

Write-Host "✅ State machine created: $STATE_MACHINE_ARN" -ForegroundColor Green
Set-Content -Path "state-machine-arn.txt" -Value $STATE_MACHINE_ARN

Remove-Item sfn-trust-policy.json, sfn-policy.json

Write-Host "`n✅ Step Functions deployed!" -ForegroundColor Green
