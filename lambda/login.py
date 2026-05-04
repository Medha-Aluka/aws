import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('login')

# Restrict CORS to the S3-hosted frontend origin only (security best practice)
CORS_ORIGIN = 'http://music-app-website-s4154047.s3-website-us-east-1.amazonaws.com'

HEADERS = {
    'Access-Control-Allow-Origin':  CORS_ORIGIN,
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST,OPTIONS'
}

def lambda_handler(event, context):
    body = json.loads(event['body'])
    email    = body.get('email', '').strip()
    password = body.get('password', '').strip()

    response = table.get_item(Key={'email': email})
    user = response.get('Item')

    if user and user['password'] == password:
        return {
            'statusCode': 200,
            'headers': HEADERS,
            'body': json.dumps({'success': True, 'user_name': user['user_name'], 'email': email})
        }
    return {
        'statusCode': 401,
        'headers': HEADERS,
        'body': json.dumps({'success': False, 'message': 'email or password is invalid'})
    }
