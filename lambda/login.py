import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('login')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    email    = body.get('email', '').strip()
    password = body.get('password', '').strip()

    response = table.get_item(Key={'email': email})
    user = response.get('Item')

    if user and user['password'] == password:
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({'success': True, 'user_name': user['user_name'], 'email': email})
        }
    return {
        'statusCode': 401,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps({'success': False, 'message': 'email or password is invalid'})
    }
