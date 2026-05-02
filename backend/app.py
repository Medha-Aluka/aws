from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
from boto3.dynamodb.conditions import Key, Attr
import json

app = Flask(__name__)
CORS(app)  

BUCKET_NAME = 'music-app-images-s4154047'
REGION = 'us-east-1'

dynamodb = boto3.resource('dynamodb', region_name=REGION)
s3_client = boto3.client('s3', region_name=REGION)

login_table = dynamodb.Table('login')
music_table = dynamodb.Table('music')
sub_table   = dynamodb.Table('subscriptions')


def get_presigned_url(image_url):
    """Generate a secure presigned URL for an S3 image (valid 1 hour)"""
    filename = image_url.split('/')[-1]
    return s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': f'artist-images/{filename}'},
        ExpiresIn=3600
    )


# ──────────────────────────────────────────────
# POST /login
# Checks email + password against login table
# ──────────────────────────────────────────────
@app.route('/login', methods=['POST'])
def login():
    body = request.get_json()
    email    = body.get('email', '').strip()
    password = body.get('password', '').strip()

    # Use get_item (Query by primary key - most efficient)
    response = login_table.get_item(Key={'email': email})
    user = response.get('Item')

    if user and user['password'] == password:
        return jsonify({'success': True, 'user_name': user['user_name'], 'email': email})
    return jsonify({'success': False, 'message': 'email or password is invalid'}), 401


# ──────────────────────────────────────────────
# POST /register
# Adds a new user to the login table
# ──────────────────────────────────────────────
@app.route('/register', methods=['POST'])
def register():
    body     = request.get_json()
    email    = body.get('email', '').strip()
    username = body.get('user_name', '').strip()
    password = body.get('password', '').strip()

    # Check if email already exists
    response = login_table.get_item(Key={'email': email})
    if 'Item' in response:
        return jsonify({'success': False, 'message': 'The email already exists'}), 409

    # Add new user
    login_table.put_item(Item={'email': email, 'user_name': username, 'password': password})
    return jsonify({'success': True, 'message': 'Registration successful'})


# ──────────────────────────────────────────────
# GET /songs title = &artist = &year =&album =
# Query music table - uses Query or Scan depending on fields provided
# ──────────────────────────────────────────────
@app.route('/songs', methods=['GET'])
def query_songs():
    title  = request.args.get('title',  '').strip()
    artist = request.args.get('artist', '').strip()
    year   = request.args.get('year',   '').strip()
    album  = request.args.get('album',  '').strip()

    if not any([title, artist, year, album]):
        return jsonify({'message': 'Please provide at least one search field'}), 400

    items = []

    # Uses the most efficient retrieval method based on what fields are provided:
    if artist and year:
        # LSI: artist-year-index → Query (efficient)
        resp = music_table.query(
            IndexName='artist-year-index',
            KeyConditionExpression=Key('artist').eq(artist) & Key('year').eq(year)
        )
        items = resp['Items']

    elif artist:
        # Base is table Query by partition key (most efficient)
        resp = music_table.query(
            KeyConditionExpression=Key('artist').eq(artist)
        )
        items = resp['Items']

    elif year:
        # GSI: year-artist-index → Query (efficient)
        resp = music_table.query(
            IndexName='year-artist-index',
            KeyConditionExpression=Key('year').eq(year)
        )
        items = resp['Items']

    else:
        # Only title or album given → must uses Scan with filter
        filters = []
        if title:
            filters.append(Attr('title').eq(title))
        if album:
            filters.append(Attr('album').eq(album))
        combined = filters[0]
        for f in filters[1:]:
            combined = combined & f
        resp = music_table.scan(FilterExpression=combined)
        items = resp['Items']

    # Applies remaining filters on the result set
    if title and artist:
        items = [i for i in items if i['title'] == title]
    if album and (artist or year):
        items = [i for i in items if i['album'] == album]
    if title and year:
        items = [i for i in items if i['title'] == title]

    if not items:
        return jsonify({'results': [], 'message': 'No result is retrieved. Please query again'})

    # Attach secure S3 presigned URLs for images
    for item in items:
        item['s3_image_url'] = get_presigned_url(item['image_url'])

    return jsonify({'results': items})


# ──────────────────────────────────────────────
# GET /subscriptions email =
# Get all subscriptions for a logged in user
# ──────────────────────────────────────────────
@app.route('/subscriptions', methods=['GET'])
def get_subscriptions():
    email = request.args.get('email', '').strip()
    if not email:
        return jsonify({'subscriptions': []})

    resp = sub_table.query(
        KeyConditionExpression=Key('email').eq(email)
    )
    items = resp['Items']

    for item in items:
        item['s3_image_url'] = get_presigned_url(item['image_url'])

    return jsonify({'subscriptions': items})


# ──────────────────────────────────────────────
# POST /subscribe
# Add a song to a user's subscriptions
# ──────────────────────────────────────────────
@app.route('/subscribe', methods=['POST'])
def subscribe():
    body = request.get_json()
    sub_table.put_item(Item={
        'email':     body['email'],
        'song_key':  f"{body['title']}#{body['album']}",
        'title':     body['title'],
        'artist':    body['artist'],
        'year':      body['year'],
        'album':     body['album'],
        'image_url': body['image_url']
    })
    return jsonify({'success': True})


# ──────────────────────────────────────────────
# DELETE /unsubscribe
# Remove a song from a user's subscriptions
# ──────────────────────────────────────────────
@app.route('/unsubscribe', methods=['DELETE'])
def unsubscribe():
    body = request.get_json()
    sub_table.delete_item(Key={
        'email':    body['email'],
        'song_key': body['song_key']
    })
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
