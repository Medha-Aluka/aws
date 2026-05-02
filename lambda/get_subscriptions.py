import boto3
import json
from boto3.dynamodb.conditions import Key

dynamodb  = boto3.resource('dynamodb')
s3_client = boto3.client('s3', region_name='us-east-1')
table     = dynamodb.Table('subscriptions')

BUCKET_NAME = 'music-app-images-s4154047'

def get_presigned_url(image_url):
    filename = image_url.split('/')[-1]
    return s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': f'artist-images/{filename}'},
        ExpiresIn=3600
    )

def lambda_handler(event, context):
    params = event.get('queryStringParameters') or {}
    email  = params.get('email', '').strip()

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }

    if not email:
        return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'subscriptions': []})}

    resp  = table.query(KeyConditionExpression=Key('email').eq(email))
    items = resp['Items']

    for item in items:
        item['s3_image_url'] = get_presigned_url(item['image_url'])

    return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'subscriptions': items})}
