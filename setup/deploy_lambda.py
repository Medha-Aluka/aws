import boto3
import zipfile
import os
import json

REGION      = 'us-east-1'
ACCOUNT_ID  = '436406244062'
ROLE_ARN    = f'arn:aws:iam::{ACCOUNT_ID}:role/LabRole'
LAMBDA_DIR  = os.path.join(os.path.dirname(__file__), '../lambda')

lambda_client = boto3.client('lambda', region_name=REGION)

# Each Lambda function: (function_name, filename)
functions = [
    ('music-login',              'login.py'),
    ('music-register',           'register.py'),
    ('music-query-songs',        'query_songs.py'),
    ('music-get-subscriptions',  'get_subscriptions.py'),
    ('music-subscribe',          'subscribe.py'),
    ('music-unsubscribe',        'unsubscribe.py'),
]

def zip_file(py_file, zip_path):
    """Zip a single Python file for Lambda deployment"""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(py_file, os.path.basename(py_file))

def deploy_function(name, filename):
    py_path  = os.path.join(LAMBDA_DIR, filename)
    zip_path = os.path.join(LAMBDA_DIR, filename.replace('.py', '.zip'))

    # Zip the file
    zip_file(py_path, zip_path)
    with open(zip_path, 'rb') as f:
        zip_bytes = f.read()

    try:
        # Try to create new function
        lambda_client.create_function(
            FunctionName=name,
            Runtime='python3.12',
            Role=ROLE_ARN,
            Handler=filename.replace('.py', '.lambda_handler'),
            Code={'ZipFile': zip_bytes},
            Timeout=30,
            MemorySize=128,
        )
        print(f"  Created: {name}")
    except lambda_client.exceptions.ResourceConflictException:
        # Already exists — update the code instead
        lambda_client.update_function_code(
            FunctionName=name,
            ZipFile=zip_bytes,
        )
        print(f"  Updated: {name}")

    # Clean up zip
    os.remove(zip_path)

print("Deploying Lambda functions...\n")
for func_name, func_file in functions:
    deploy_function(func_name, func_file)

print("\nAll Lambda functions deployed!")
print("\nFunction ARNs:")
for func_name, _ in functions:
    resp = lambda_client.get_function(FunctionName=func_name)
    print(f"  {func_name}: {resp['Configuration']['FunctionArn']}")
