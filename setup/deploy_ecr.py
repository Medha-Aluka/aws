import boto3
import subprocess
import json
import os

REGION     = 'us-east-1'
ACCOUNT_ID = '436406244062'
REPO_NAME  = 'music-app'

ecr = boto3.client('ecr', region_name=REGION)

# step 1: Create ECR repository
print("Creating ECR repository...")
try:
    resp = ecr.create_repository(repositoryName=REPO_NAME)
    repo_uri = resp['repository']['repositoryUri']
    print(f"  Created: {repo_uri}")
except ecr.exceptions.RepositoryAlreadyExistsException:
    resp = ecr.describe_repositories(repositoryNames=[REPO_NAME])
    repo_uri = resp['repositories'][0]['repositoryUri']
    print(f"  Already exists: {repo_uri}")

# Step 2: Get ECR login token and login Docker
print("\nLogging Docker into ECR...")
token = ecr.get_authorization_token()
auth = token['authorizationData'][0]
ecr_endpoint = auth['proxyEndpoint']

result = subprocess.run(
    f'aws ecr get-login-password --region {REGION} | docker login --username AWS --password-stdin {ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com',
    shell=True, capture_output=True, text=True
)
if result.returncode == 0:
    print("  Docker logged in to ECR!")
else:
    print(f"  Login output: {result.stdout} {result.stderr}")

backend_dir = os.path.join(os.path.dirname(__file__), '../backend')
backend_dir = os.path.abspath(backend_dir)
print(f"\nBuilding Docker image from: {backend_dir}")

result = subprocess.run(
    f'docker build -t {REPO_NAME} "{backend_dir}"',
    shell=True, capture_output=False
)
if result.returncode != 0:
    print("ERROR: Docker build failed!")
    exit(1)
print("  Docker image built!")

# Step 4: Tagging and push image to ECR 
print("\nTagging image...")
subprocess.run(f'docker tag {REPO_NAME}:latest {repo_uri}:latest', shell=True)

print("Pushing image to ECR (this takes 1-2 minutes)...")
result = subprocess.run(f'docker push {repo_uri}:latest', shell=True, capture_output=False)
if result.returncode != 0:
    print("ERROR: Docker push failed!")
    exit(1)

print(f"\n{'='*60}")
print(f"IMAGE PUSHED TO ECR!")
print(f"Image URI: {repo_uri}:latest")
print(f"{'='*60}")

with open(os.path.join(os.path.dirname(__file__), 'ecr_uri.txt'), 'w') as f:
    f.write(repo_uri)
print("\nSaved image URI to ecr_uri.txt")
print("Now run: python deploy_ecs.py")
