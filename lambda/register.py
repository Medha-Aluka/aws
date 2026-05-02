import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('login')

def lambda_handler(event, context):
    body     = json.loads(event['body'])
    email    = body.get('email', '').strip()
    username = body.get('user_name', '').strip()
    password = body.get('password', '').strip()

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }

    # Check if email already exists
    response = table.get_item(Key={'email': email})
    if 'Item' in response:
        return {
            'statusCode': 409,
            'headers': headers,
            'body': json.dumps({'success': False, 'message': 'The email already exists'})
        }

    # Add new user
    table.put_item(Item={'email': email, 'user_name': username, 'password': password})
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'success': True, 'message': 'Registration successful'})
    }
