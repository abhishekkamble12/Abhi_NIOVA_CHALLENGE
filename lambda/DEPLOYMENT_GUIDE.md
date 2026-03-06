# Lambda Functions Deployment Configuration

## Folder Structure

```
lambda/
├── functions/              # Individual Lambda function handlers
│   ├── article_create.py
│   ├── article_get.py
│   ├── article_list.py
│   ├── article_search.py
│   ├── brand_create.py
│   └── ...
│
├── shared/                 # Shared utilities (deployed as Lambda layer)
│   ├── response.py
│   └── database.py
│
└── layers/                 # Lambda layers
    ├── dependencies/       # Python dependencies layer
    │   └── requirements.txt
    └── app-code/          # Application code layer
        └── python/
            └── app/       # Copy of backend/app
```

## Lambda Layer: Dependencies

**File:** `lambda/layers/dependencies/requirements.txt`

```
sqlalchemy==2.0.23
asyncpg==0.29.0
psycopg2-binary==2.9.9
boto3==1.34.0
pydantic==2.5.0
sentence-transformers==2.2.2
```

**Build Command:**
```bash
cd lambda/layers/dependencies
pip install -r requirements.txt -t python/
zip -r dependencies-layer.zip python/
```

## Lambda Layer: Application Code

**Structure:**
```
lambda/layers/app-code/
└── python/
    ├── app/
    │   ├── models/
    │   ├── services/
    │   └── schemas/
    └── shared/
        ├── response.py
        └── database.py
```

**Build Command:**
```bash
cd lambda/layers/app-code
# Copy backend code
cp -r ../../../backend/app python/
cp -r ../../shared python/
zip -r app-code-layer.zip python/
```

## Lambda Function Configuration

### Article Create Function

```yaml
FunctionName: hivemind-article-create
Runtime: python3.11
Handler: article_create.handler
MemorySize: 1024
Timeout: 30
Environment:
  Variables:
    DB_SECRET_NAME: hivemind/aurora/credentials
    AWS_REGION: us-east-1
Layers:
  - arn:aws:lambda:region:account:layer:dependencies:1
  - arn:aws:lambda:region:account:layer:app-code:1
VpcConfig:
  SubnetIds:
    - subnet-xxx
    - subnet-yyy
  SecurityGroupIds:
    - sg-lambda
IAM Role:
  - AWSLambdaVPCAccessExecutionRole
  - SecretsManagerReadAccess
  - RDSDataAccess
```

### Article Get Function

```yaml
FunctionName: hivemind-article-get
Runtime: python3.11
Handler: article_get.handler
MemorySize: 512
Timeout: 10
Environment:
  Variables:
    DB_SECRET_NAME: hivemind/aurora/credentials
Layers:
  - arn:aws:lambda:region:account:layer:dependencies:1
  - arn:aws:lambda:region:account:layer:app-code:1
VpcConfig:
  SubnetIds:
    - subnet-xxx
  SecurityGroupIds:
    - sg-lambda
```

### Article Search Function

```yaml
FunctionName: hivemind-article-search
Runtime: python3.11
Handler: article_search.handler
MemorySize: 1024
Timeout: 30
Environment:
  Variables:
    DB_SECRET_NAME: hivemind/aurora/credentials
    EMBEDDING_MODEL: all-MiniLM-L6-v2
Layers:
  - arn:aws:lambda:region:account:layer:dependencies:1
  - arn:aws:lambda:region:account:layer:app-code:1
VpcConfig:
  SubnetIds:
    - subnet-xxx
  SecurityGroupIds:
    - sg-lambda
```

## API Gateway Integration

### REST API Configuration

```yaml
API Name: HiveMind API
Stage: prod
Endpoint Type: Regional

Resources:
  /articles:
    POST:
      Integration: Lambda (hivemind-article-create)
      Authorization: Cognito User Pool
      Request Validation: Validate body
    
    GET:
      Integration: Lambda (hivemind-article-list)
      Authorization: None (public)
      Request Validation: Validate query parameters
  
  /articles/{article_id}:
    GET:
      Integration: Lambda (hivemind-article-get)
      Authorization: None (public)
      Request Validation: Validate path parameters
  
  /articles/search/semantic:
    GET:
      Integration: Lambda (hivemind-article-search)
      Authorization: None (public)
      Request Validation: Validate query parameters
  
  /brands:
    POST:
      Integration: Lambda (hivemind-brand-create)
      Authorization: Cognito User Pool
      Request Validation: Validate body
```

### API Gateway Request Mapping

**No mapping needed** - Lambda receives full API Gateway event structure.

### API Gateway Response Mapping

**No mapping needed** - Lambda returns properly formatted response.

## Deployment with AWS SAM

**File:** `template.yaml`

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Runtime: python3.11
    Timeout: 30
    MemorySize: 1024
    Environment:
      Variables:
        DB_SECRET_NAME: !Ref DatabaseSecretName
    VpcConfig:
      SubnetIds: !Ref PrivateSubnetIds
      SecurityGroupIds:
        - !Ref LambdaSecurityGroup
    Layers:
      - !Ref DependenciesLayer
      - !Ref AppCodeLayer

Parameters:
  DatabaseSecretName:
    Type: String
    Default: hivemind/aurora/credentials
  
  PrivateSubnetIds:
    Type: CommaDelimitedList
  
  LambdaSecurityGroup:
    Type: String

Resources:
  # Lambda Layers
  DependenciesLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: hivemind-dependencies
      ContentUri: layers/dependencies/
      CompatibleRuntimes:
        - python3.11
  
  AppCodeLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: hivemind-app-code
      ContentUri: layers/app-code/
      CompatibleRuntimes:
        - python3.11
  
  # API Gateway
  HiveMindApi:
    Type: AWS::Serverless::Api
    Properties:
      Name: HiveMind API
      StageName: prod
      Cors:
        AllowOrigin: "'*'"
        AllowHeaders: "'Content-Type,Authorization'"
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
      Auth:
        DefaultAuthorizer: CognitoAuthorizer
        Authorizers:
          CognitoAuthorizer:
            UserPoolArn: !GetAtt UserPool.Arn
  
  # Lambda Functions
  ArticleCreateFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: hivemind-article-create
      CodeUri: functions/
      Handler: article_create.handler
      Events:
        CreateArticle:
          Type: Api
          Properties:
            RestApiId: !Ref HiveMindApi
            Path: /articles
            Method: POST
  
  ArticleGetFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: hivemind-article-get
      CodeUri: functions/
      Handler: article_get.handler
      MemorySize: 512
      Timeout: 10
      Events:
        GetArticle:
          Type: Api
          Properties:
            RestApiId: !Ref HiveMindApi
            Path: /articles/{article_id}
            Method: GET
            Auth:
              Authorizer: NONE
  
  ArticleListFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: hivemind-article-list
      CodeUri: functions/
      Handler: article_list.handler
      MemorySize: 512
      Events:
        ListArticles:
          Type: Api
          Properties:
            RestApiId: !Ref HiveMindApi
            Path: /articles
            Method: GET
            Auth:
              Authorizer: NONE
  
  ArticleSearchFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: hivemind-article-search
      CodeUri: functions/
      Handler: article_search.handler
      Events:
        SearchArticles:
          Type: Api
          Properties:
            RestApiId: !Ref HiveMindApi
            Path: /articles/search/semantic
            Method: GET
            Auth:
              Authorizer: NONE
  
  BrandCreateFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: hivemind-brand-create
      CodeUri: functions/
      Handler: brand_create.handler
      Events:
        CreateBrand:
          Type: Api
          Properties:
            RestApiId: !Ref HiveMindApi
            Path: /brands
            Method: POST

Outputs:
  ApiUrl:
    Description: API Gateway URL
    Value: !Sub 'https://${HiveMindApi}.execute-api.${AWS::Region}.amazonaws.com/prod'
```

## Deployment Commands

```bash
# Build layers
cd lambda/layers/dependencies
pip install -r requirements.txt -t python/
cd ../../..

# Deploy with SAM
sam build
sam deploy --guided

# Or deploy with AWS CLI
aws lambda create-function \
  --function-name hivemind-article-create \
  --runtime python3.11 \
  --handler article_create.handler \
  --role arn:aws:iam::account:role/lambda-execution-role \
  --code S3Bucket=my-bucket,S3Key=article_create.zip \
  --layers arn:aws:lambda:region:account:layer:dependencies:1 \
  --vpc-config SubnetIds=subnet-xxx,SecurityGroupIds=sg-xxx
```

## Testing Lambda Functions Locally

```bash
# Install SAM CLI
pip install aws-sam-cli

# Invoke function locally
sam local invoke ArticleCreateFunction \
  --event events/article-create.json

# Start local API
sam local start-api
curl http://localhost:3000/articles
```

## Environment Variables

```bash
# Required for all functions
DB_SECRET_NAME=hivemind/aurora/credentials
AWS_REGION=us-east-1

# Required for embedding functions
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_DIMENSION=384

# Optional
LOG_LEVEL=INFO
ENVIRONMENT=production
```

## IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:hivemind/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface"
      ],
      "Resource": "*"
    }
  ]
}
```
