import boto3
import json

dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table('subscriptions')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }
    table.put_item(Item={
        'email':     body['email'],
        'song_key':  f"{body['title']}#{body['album']}",
        'title':     body['title'],
        'artist':    body['artist'],
        'year':      body['year'],
        'album':     body['album'],
        'image_url': body['image_url']
    })
    return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'success': True})}
