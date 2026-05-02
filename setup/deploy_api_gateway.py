import boto3
import json
import time

REGION     = 'us-east-1'
ACCOUNT_ID = '436406244062'

apigw  = boto3.client('apigateway',  region_name=REGION)
lambda_client = boto3.client('lambda', region_name=REGION)

# Step 1: Create REST API
print("Creating API Gateway REST API...")
api = apigw.create_rest_api(
    name='music-api',
    description='Music Subscription App API',
    endpointConfiguration={'types': ['REGIONAL']}
)
api_id = api['id']
print(f"  API ID: {api_id}")

# Get root resource ID
resources = apigw.get_resources(restApiId=api_id)
root_id   = [r for r in resources['items'] if r['path'] == '/'][0]['id']

def make_lambda_uri(function_name):
    return (f"arn:aws:apigateway:{REGION}:lambda:path/2015-03-31/functions/"
            f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:{function_name}/invocations")

def add_cors(resource_id):
    """Add OPTIONS method for CORS preflight"""
    try:
        apigw.put_method(
            restApiId=api_id, resourceId=resource_id,
            httpMethod='OPTIONS', authorizationType='NONE'
        )
        apigw.put_integration(
            restApiId=api_id, resourceId=resource_id,
            httpMethod='OPTIONS', type='MOCK',
            requestTemplates={'application/json': '{"statusCode": 200}'}
        )
        apigw.put_method_response(
            restApiId=api_id, resourceId=resource_id,
            httpMethod='OPTIONS', statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': False,
                'method.response.header.Access-Control-Allow-Methods': False,
                'method.response.header.Access-Control-Allow-Origin':  False,
            }
        )
        apigw.put_integration_response(
            restApiId=api_id, resourceId=resource_id,
            httpMethod='OPTIONS', statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key'",
                'method.response.header.Access-Control-Allow-Methods': "'GET,POST,DELETE,OPTIONS'",
                'method.response.header.Access-Control-Allow-Origin':  "'*'",
            }
        )
    except Exception as e:
        print(f"    CORS options warning: {e}")

def add_method(resource_id, http_method, function_name):
    """Add a method and connect it to a Lambda function"""
    lambda_uri = make_lambda_uri(function_name)

    apigw.put_method(
        restApiId=api_id, resourceId=resource_id,
        httpMethod=http_method, authorizationType='NONE'
    )
    apigw.put_integration(
        restApiId=api_id, resourceId=resource_id,
        httpMethod=http_method,
        type='AWS_PROXY',
        integrationHttpMethod='POST',  # Lambda always uses POST internally
        uri=lambda_uri
    )
    # Allow API Gateway to invoke this Lambda
    try:
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=f'apigateway-{http_method}-{function_name}-{int(time.time())}',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f'arn:aws:execute-api:{REGION}:{ACCOUNT_ID}:{api_id}/*/{http_method}/*'
        )
    except Exception as e:
        print(f"    Permission warning: {e}")

#  Step 2: Create each resource and method
routes = [
    # (path,             http_method, lambda_function_name)
    ('/login',           'POST',   'music-login'),
    ('/register',        'POST',   'music-register'),
    ('/songs',           'GET',    'music-query-songs'),
    ('/subscriptions',   'GET',    'music-get-subscriptions'),
    ('/subscribe',       'POST',   'music-subscribe'),
    ('/unsubscribe',     'DELETE', 'music-unsubscribe'),
]

print("\nCreating resources and methods...")
for path, method, func in routes:
    resource_name = path.strip('/')

    # Create the resource (e.g. /login)
    resource = apigw.create_resource(
        restApiId=api_id,
        parentId=root_id,
        pathPart=resource_name
    )
    resource_id = resource['id']

    # Add the main method
    add_method(resource_id, method, func)
    print(f"  {method:6} {path} → {func}")

    # Add CORS OPTIONS
    add_cors(resource_id)

#  Step 3: Deploy to 'prod' stage
print("\nDeploying API to 'prod' stage...")
deployment = apigw.create_deployment(
    restApiId=api_id,
    stageName='prod',
    stageDescription='Production stage'
)

invoke_url = f"https://{api_id}.execute-api.{REGION}.amazonaws.com/prod"
print(f"\nAPI Gateway deployed!")
print(f"\n{'='*60}")
print(f"YOUR API URL:")
print(f"{invoke_url}")
print(f"{'='*60}")
print(f"\nSave this URL — you need it in your HTML files!")
print(f"\nTest endpoints:")
print(f"  POST   {invoke_url}/login")
print(f"  POST   {invoke_url}/register")
print(f"  GET    {invoke_url}/songs?artist=Taylor+Swift")
print(f"  GET    {invoke_url}/subscriptions?email=test@test.com")
print(f"  POST   {invoke_url}/subscribe")
print(f"  DELETE {invoke_url}/unsubscribe")
