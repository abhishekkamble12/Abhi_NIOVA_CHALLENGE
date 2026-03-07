# Enable CORS on API Gateway

$API_ID = "wcp5c3ga8b"
$REGION = "ap-south-1"

Write-Host " Enabling CORS on API Gateway" -ForegroundColor Cyan
Write-Host ""

# Get all resources
Write-Host "[1/2] Getting API resources..." -ForegroundColor Yellow
$resources = aws apigateway get-resources --rest-api-id $API_ID --region $REGION | ConvertFrom-Json

Write-Host " Found $($resources.items.Count) resources" -ForegroundColor Green

# Enable CORS for each resource
Write-Host ""
Write-Host "[2/2] Enabling CORS..." -ForegroundColor Yellow

foreach ($resource in $resources.items) {
    $resourceId = $resource.id
    $path = $resource.path
    
    Write-Host "  → $path" -ForegroundColor Gray
    
    # Add OPTIONS method
    aws apigateway put-method `
        --rest-api-id $API_ID `
        --resource-id $resourceId `
        --http-method OPTIONS `
        --authorization-type NONE `
        --region $REGION 2>$null
    
    # Add mock integration
    aws apigateway put-integration `
        --rest-api-id $API_ID `
        --resource-id $resourceId `
        --http-method OPTIONS `
        --type MOCK `
        --request-templates '{"application/json":"{\"statusCode\":200}"}' `
        --region $REGION 2>$null
    
    # Add method response
    aws apigateway put-method-response `
        --rest-api-id $API_ID `
        --resource-id $resourceId `
        --http-method OPTIONS `
        --status-code 200 `
        --response-parameters '{\"method.response.header.Access-Control-Allow-Headers\":false,\"method.response.header.Access-Control-Allow-Methods\":false,\"method.response.header.Access-Control-Allow-Origin\":false}' `
        --region $REGION 2>$null
    
    # Add integration response with CORS headers
    aws apigateway put-integration-response `
        --rest-api-id $API_ID `
        --resource-id $resourceId `
        --http-method OPTIONS `
        --status-code 200 `
        --response-parameters '{\"method.response.header.Access-Control-Allow-Headers\":\"'"'"'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"'"'\",\"method.response.header.Access-Control-Allow-Methods\":\"'"'"'GET,POST,PUT,DELETE,OPTIONS'"'"'\",\"method.response.header.Access-Control-Allow-Origin\":\"'"'"'*'"'"'\"}' `
        --region $REGION 2>$null
}

# Deploy API
Write-Host ""
Write-Host "Deploying API..." -ForegroundColor Yellow
aws apigateway create-deployment `
    --rest-api-id $API_ID `
    --stage-name prod `
    --region $REGION

Write-Host ""
Write-Host " CORS Enabled!" -ForegroundColor Green
Write-Host ""
Write-Host "API URL: https://$API_ID.execute-api.$REGION.amazonaws.com/prod" -ForegroundColor White
Write-Host ""
Write-Host "Test it:" -ForegroundColor Yellow
Write-Host "  Refresh your frontend and try again" -ForegroundColor Gray
