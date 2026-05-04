import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

dynamodb  = boto3.resource('dynamodb')
s3_client = boto3.client('s3', region_name='us-east-1')
table     = dynamodb.Table('music')

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
    title  = params.get('title',  '').strip().title()
    artist = params.get('artist', '').strip().title()
    year   = params.get('year',   '').strip()
    album  = params.get('album',  '').strip().title()

    # Restrict CORS to the S3-hosted frontend origin only (security best practice)
    headers = {
        'Access-Control-Allow-Origin':  'http://music-app-website-s4154047.s3-website-us-east-1.amazonaws.com',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }

    if not any([title, artist, year, album]):
        return {'statusCode': 400, 'headers': headers,
                'body': json.dumps({'message': 'Please provide at least one field'})}

    items = []

    if artist and year:
        resp  = table.query(IndexName='artist-year-index',
                            KeyConditionExpression=Key('artist').eq(artist) & Key('year').eq(year))
        items = resp['Items']
    elif artist:
        resp  = table.query(KeyConditionExpression=Key('artist').eq(artist))
        items = resp['Items']
    elif year:
        resp  = table.query(IndexName='year-artist-index',
                            KeyConditionExpression=Key('year').eq(year))
        items = resp['Items']
    else:
        filters = []
        if title:
            filters.append(Attr('title').eq(title))
        if album:
            filters.append(Attr('album').eq(album))
        combined = filters[0]
        for f in filters[1:]:
            combined = combined & f
        resp  = table.scan(FilterExpression=combined)
        items = resp['Items']

    # Additional filters on Query results
    if title and artist:
        items = [i for i in items if i['title'] == title]
    if album and (artist or year):
        items = [i for i in items if i['album'] == album]
    if title and year:
        items = [i for i in items if i['title'] == title]

    if not items:
        return {'statusCode': 200, 'headers': headers,
                'body': json.dumps({'results': [], 'message': 'No result is retrieved. Please query again'})}

    for item in items:
        item['s3_image_url'] = get_presigned_url(item['image_url'])

    return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'results': items})}
