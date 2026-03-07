# Create API Gateway REST API

$REGION = "ap-south-1"
$ACCOUNT_ID = "586098609294"

Write-Host "🌐 Creating API Gateway..." -ForegroundColor Cyan

# Create REST API
$API_ID = aws apigateway create-rest-api `
    --name "HiveMind-API" `
    --description "HiveMind Social Media AI Platform" `
    --region $REGION `
    --query 'id' `
    --output text

Write-Host "✅ API created: $API_ID" -ForegroundColor Green
Set-Content -Path "api-id.txt" -Value $API_ID

# Get root resource
$ROOT_ID = aws apigateway get-resources `
    --rest-api-id $API_ID `
    --region $REGION `
    --query 'items[0].id' `
    --output text

# Create /social resource
$SOCIAL_ID = aws apigateway create-resource `
    --rest-api-id $API_ID `
    --parent-id $ROOT_ID `
    --path-part social `
    --region $REGION `
    --query 'id' `
    --output text

# Create /social/brands resource
$BRANDS_ID = aws apigateway create-resource `
    --rest-api-id $API_ID `
    --parent-id $SOCIAL_ID `
    --path-part brands `
    --region $REGION `
    --query 'id' `
    --output text

# Create /social/brands/{brand_id} resource
$BRAND_ID_RESOURCE = aws apigateway create-resource `
    --rest-api-id $API_ID `
    --parent-id $BRANDS_ID `
    --path-part "{brand_id}" `
    --region $REGION `
    --query 'id' `
    --output text

# POST /social/brands -> social_create_brand
aws apigateway put-method `
    --rest-api-id $API_ID `
    --resource-id $BRANDS_ID `
    --http-method POST `
    --authorization-type NONE `
    --region $REGION

aws apigateway put-integration `
    --rest-api-id $API_ID `
    --resource-id $BRANDS_ID `
    --http-method POST `
    --type AWS_PROXY `
    --integration-http-method POST `
    --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:hivemind-social-create-brand/invocations" `
    --region $REGION

# GET /social/brands -> social_list_brands
aws apigateway put-method `
    --rest-api-id $API_ID `
    --resource-id $BRANDS_ID `
    --http-method GET `
    --authorization-type NONE `
    --region $REGION

aws apigateway put-integration `
    --rest-api-id $API_ID `
    --resource-id $BRANDS_ID `
    --http-method GET `
    --type AWS_PROXY `
    --integration-http-method POST `
    --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:hivemind-social-list-brands/invocations" `
    --region $REGION

# GET /social/brands/{brand_id} -> social_get_brand
aws apigateway put-method `
    --rest-api-id $API_ID `
    --resource-id $BRAND_ID_RESOURCE `
    --http-method GET `
    --authorization-type NONE `
    --region $REGION

aws apigateway put-integration `
    --rest-api-id $API_ID `
    --resource-id $BRAND_ID_RESOURCE `
    --http-method GET `
    --type AWS_PROXY `
    --integration-http-method POST `
    --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:hivemind-social-get-brand/invocations" `
    --region $REGION

# Grant Lambda permissions
$functions = @(
    @{Name="hivemind-social-create-brand"; Resource=$BRANDS_ID; Method="POST"},
    @{Name="hivemind-social-list-brands"; Resource=$BRANDS_ID; Method="GET"},
    @{Name="hivemind-social-get-brand"; Resource=$BRAND_ID_RESOURCE; Method="GET"}
)

foreach ($func in $functions) {
    aws lambda add-permission `
        --function-name $func.Name `
        --statement-id "apigateway-$($func.Method)-$(Get-Random)" `
        --action lambda:InvokeFunction `
        --principal apigateway.amazonaws.com `
        --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/$($func.Method)/*" `
        --region $REGION 2>$null
}

# Deploy API
aws apigateway create-deployment `
    --rest-api-id $API_ID `
    --stage-name prod `
    --region $REGION

$API_URL = "https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod"
Write-Host "`n✅ API Gateway deployed!" -ForegroundColor Green
Write-Host "API URL: $API_URL" -ForegroundColor White
Set-Content -Path "api-url.txt" -Value $API_URL
