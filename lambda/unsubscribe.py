import boto3
import json

dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table('subscriptions')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'DELETE,OPTIONS'
    }
    table.delete_item(Key={
        'email':    body['email'],
        'song_key': body['song_key']
    })
    return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'success': True})}
