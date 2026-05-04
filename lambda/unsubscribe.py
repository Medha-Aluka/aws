import boto3
import json

dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table('subscriptions')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    # Restrict CORS to the S3-hosted frontend origin only (security best practice)
    headers = {
        'Access-Control-Allow-Origin':  'http://music-app-website-s4154047.s3-website-us-east-1.amazonaws.com',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'DELETE,OPTIONS'
    }
    table.delete_item(Key={
        'email':    body['email'],
        'song_key': body['song_key']
    })
    return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'success': True})}
