# Connect Lambda Functions to API Gateway

$API_ID = "wcp5c3ga8b"
$REGION = "ap-south-1"
$ACCOUNT_ID = "150809276128"

Write-Host "Connecting Lambda to API Gateway" -ForegroundColor Cyan
Write-Host ""

# Get existing resources
$resources = aws apigateway get-resources --rest-api-id $API_ID --region $REGION | ConvertFrom-Json

# Find resource IDs
$brandsResource = ($resources.items | Where-Object { $_.path -eq "/social/brands" }).id
$brandIdResource = ($resources.items | Where-Object { $_.path -eq "/social/brands/{brand_id}" }).id

Write-Host "Resources found:" -ForegroundColor Yellow
Write-Host "  /social/brands: $brandsResource" -ForegroundColor Gray
Write-Host "  /social/brands/{brand_id}: $brandIdResource" -ForegroundColor Gray
Write-Host ""

# Update integrations
Write-Host "Updating Lambda integrations..." -ForegroundColor Yellow

# POST /social/brands -> social_create_brand
Write-Host "  POST /social/brands -> hivemind-social-create-brand" -ForegroundColor Gray
aws apigateway put-integration `
    --rest-api-id $API_ID `
    --resource-id $brandsResource `
    --http-method POST `
    --type AWS_PROXY `
    --integration-http-method POST `
    --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:hivemind-social-create-brand/invocations" `
    --region $REGION

# GET /social/brands -> social_list_brands
Write-Host "  GET /social/brands -> hivemind-social-list-brands" -ForegroundColor Gray
aws apigateway put-integration `
    --rest-api-id $API_ID `
    --resource-id $brandsResource `
    --http-method GET `
    --type AWS_PROXY `
    --integration-http-method POST `
    --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:hivemind-social-list-brands/invocations" `
    --region $REGION

# GET /social/brands/{brand_id} -> social_get_brand
Write-Host "  GET /social/brands/{brand_id} -> hivemind-social-get-brand" -ForegroundColor Gray
aws apigateway put-integration `
    --rest-api-id $API_ID `
    --resource-id $brandIdResource `
    --http-method GET `
    --type AWS_PROXY `
    --integration-http-method POST `
    --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:hivemind-social-get-brand/invocations" `
    --region $REGION

Write-Host ""
Write-Host "Granting Lambda permissions..." -ForegroundColor Yellow

# Grant permissions
aws lambda add-permission `
    --function-name hivemind-social-create-brand `
    --statement-id apigateway-post-brands `
    --action lambda:InvokeFunction `
    --principal apigateway.amazonaws.com `
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/POST/social/brands" `
    --region $REGION 2>$null

aws lambda add-permission `
    --function-name hivemind-social-list-brands `
    --statement-id apigateway-get-brands `
    --action lambda:InvokeFunction `
    --principal apigateway.amazonaws.com `
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/GET/social/brands" `
    --region $REGION 2>$null

aws lambda add-permission `
    --function-name hivemind-social-get-brand `
    --statement-id apigateway-get-brand-id `
    --action lambda:InvokeFunction `
    --principal apigateway.amazonaws.com `
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/GET/social/brands/*" `
    --region $REGION 2>$null

Write-Host ""
Write-Host "Deploying API..." -ForegroundColor Yellow
aws apigateway create-deployment `
    --rest-api-id $API_ID `
    --stage-name prod `
    --description "Connect Lambda functions" `
    --region $REGION

Write-Host ""
Write-Host " API Gateway Connected!" -ForegroundColor Green
Write-Host ""
Write-Host "API URL: https://$API_ID.execute-api.$REGION.amazonaws.com/prod" -ForegroundColor White
Write-Host ""
Write-Host "Test endpoints:" -ForegroundColor Yellow
Write-Host "  curl https://$API_ID.execute-api.$REGION.amazonaws.com/prod/social/brands" -ForegroundColor Gray
