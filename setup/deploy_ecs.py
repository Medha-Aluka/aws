import boto3
import json
import os
import time

REGION     = 'us-east-1'
ACCOUNT_ID = '436406244062'
CLUSTER    = 'music-app-cluster'
SERVICE    = 'music-app-service'
TASK_DEF   = 'music-app-task'
LAB_ROLE   = f'arn:aws:iam::{ACCOUNT_ID}:role/LabRole'

ecs = boto3.client('ecs', region_name=REGION)
ec2 = boto3.client('ec2', region_name=REGION)
iam = boto3.client('iam', region_name=REGION)

# Create ECS service linked role if it doesn't exist
print("Ensuring ECS service linked role exists...")
try:
    iam.create_service_linked_role(AWSServiceName='ecs.amazonaws.com')
    print("  ECS service linked role created!")
    time.sleep(10)  # Wait for role to propagate
except Exception as e:
    if 'already exists' in str(e) or 'has been taken' in str(e):
        print("  ECS service linked role already exists!")
    else:
        print(f"  Note: {e}")

# Load ECR image URI saved by deploy_ecr.py
uri_file = os.path.join(os.path.dirname(__file__), 'ecr_uri.txt')
with open(uri_file) as f:
    IMAGE_URI = f.read().strip() + ':latest'
print(f"Using image: {IMAGE_URI}")

# Step 1: Create ECS Cluster
print("\nCreating ECS cluster...")
ecs.create_cluster(clusterName=CLUSTER)
print(f"  Cluster '{CLUSTER}' ready!")

#Step 2: Register Task Definition
print("\nRegistering task definition...")
task_def = {
    'family': TASK_DEF,
    'networkMode': 'awsvpc',
    'requiresCompatibilities': ['FARGATE'],
    'cpu': '256',
    'memory': '512',
    'executionRoleArn': LAB_ROLE,
    'taskRoleArn': LAB_ROLE,
    'containerDefinitions': [{
        'name': 'music-app',
        'image': IMAGE_URI,
        'portMappings': [{'containerPort': 80, 'protocol': 'tcp'}],
        'essential': True,
        'logConfiguration': {
            'logDriver': 'awslogs',
            'options': {
                'awslogs-group':         '/ecs/music-app',
                'awslogs-region':        REGION,
                'awslogs-stream-prefix': 'ecs',
                'awslogs-create-group':  'true'
            }
        }
    }]
}
resp = ecs.register_task_definition(**task_def)
task_arn = resp['taskDefinition']['taskDefinitionArn']
print(f"  Task definition registered!")

# Step 3: Get default VPC and subnets
print("\nFinding default VPC and subnets...")
vpcs = ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
vpc_id = vpcs['Vpcs'][0]['VpcId']

subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
subnet_ids = [s['SubnetId'] for s in subnets['Subnets'][:2]]
print(f"  VPC: {vpc_id}, Subnets: {subnet_ids}")

# Step 4: Create Security Group for ECS
print("\nCreating security group...")
try:
    sg = ec2.create_security_group(
        GroupName='music-ecs-sg',
        Description='Music app ECS security group',
        VpcId=vpc_id
    )
    sg_id = sg['GroupId']
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[{
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }]
    )
    print(f"  Security group created: {sg_id}")
except ec2.exceptions.ClientError as e:
    if 'already exists' in str(e):
        sgs = ec2.describe_security_groups(
            Filters=[{'Name': 'group-name', 'Values': ['music-ecs-sg']}]
        )
        sg_id = sgs['SecurityGroups'][0]['GroupId']
        print(f"  Using existing security group: {sg_id}")
    else:
        raise

# Step 5: Create ECS Service
print("\nCreating ECS service (Fargate)...")
try:
    svc = ecs.create_service(
        cluster=CLUSTER,
        serviceName=SERVICE,
        taskDefinition=TASK_DEF,
        desiredCount=1,
        launchType='FARGATE',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': subnet_ids,
                'securityGroups': [sg_id],
                'assignPublicIp': 'ENABLED'
            }
        }
    )
    print("  ECS service created!")
except ecs.exceptions.InvalidParameterException as e:
    if 'service linked role' in str(e).lower():
        print("  Service linked role issue - trying with explicit role...")
        svc = ecs.create_service(
            cluster=CLUSTER,
            serviceName=SERVICE,
            taskDefinition=TASK_DEF,
            desiredCount=1,
            launchType='FARGATE',
            role='',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': subnet_ids,
                    'securityGroups': [sg_id],
                    'assignPublicIp': 'ENABLED'
                }
            }
        )
        print("  ECS service created!")
    else:
        raise
except Exception as e:
    if 'already exists' in str(e):
        print("  Service already exists, continuing...")
    else:
        print(f"  Service error: {e}")
        raise

# Step 6: Wait for task to start and get public IP 
print("\nWaiting for ECS task to start (this takes ~2 minutes)...")
time.sleep(30)

for attempt in range(12):
    tasks = ecs.list_tasks(cluster=CLUSTER, serviceName=SERVICE)
    if tasks['taskArns']:
        task_details = ecs.describe_tasks(cluster=CLUSTER, tasks=tasks['taskArns'])
        task = task_details['tasks'][0]
        status = task.get('lastStatus', 'PENDING')
        print(f"  Task status: {status}")

        if status == 'RUNNING':
            # Get ENI and public IP
            for att in task.get('attachments', []):
                for detail in att.get('details', []):
                    if detail['name'] == 'networkInterfaceId':
                        eni_id = detail['value']
                        eni = ec2.describe_network_interfaces(NetworkInterfaceIds=[eni_id])
                        public_ip = eni['NetworkInterfaces'][0].get('Association', {}).get('PublicIp', 'N/A')
                        print(f"\n{'='*60}")
                        print(f"ECS BACKEND IS LIVE!")
                        print(f"Public IP: {public_ip}")
                        print(f"ECS URL: http://{public_ip}")
                        print(f"Test: http://{public_ip}/subscriptions?email=s41540470@student.rmit.edu.au")
                        print(f"{'='*60}")
                        exit(0)
        time.sleep(15)
    else:
        print(f"  No tasks yet, waiting...")
        time.sleep(15)

print("\nTask still starting. Check ECS console in a few minutes.")
print(f"Go to: ECS → Clusters → {CLUSTER} → Tasks → click task → get Public IP")
