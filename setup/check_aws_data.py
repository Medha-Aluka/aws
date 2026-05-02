import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.client('s3', region_name='us-east-1')

print("=" * 60)
print("CHECKING ALL AWS DATA")
print("=" * 60)

#  1. LOGIN TABLE
print("\n📋 LOGIN TABLE (users who can log in):")
login_table = dynamodb.Table('login')
resp = login_table.scan()
users = resp['Items']
print(f"  Total users: {len(users)}")
for u in sorted(users, key=lambda x: x['email']):
    print(f"  {u['email']} | username: {u['user_name']} | password: {u['password']}")

# 2. MUSIC TABLE
print("\n🎵 MUSIC TABLE (songs):")
music_table = dynamodb.Table('music')
resp = music_table.scan()
songs = resp['Items']
print(f"  Total songs: {len(songs)}")
artists = sorted(set(s['artist'] for s in songs))
print(f"  Total unique artists: {len(artists)}")
print(f"  Artists: {', '.join(artists[:10])}{'...' if len(artists) > 10 else ''}")

# 3. SUBSCRIPTIONS TABLE
print("\n⭐ SUBSCRIPTIONS TABLE (user subscriptions):")
subs_table = dynamodb.Table('subscriptions')
resp = subs_table.scan()
subs = resp['Items']
print(f"  Total subscriptions: {len(subs)}")
if subs:
    for s in subs:
        print(f"  {s['email']} subscribed to: {s['title']} by {s['artist']}")
else:
    print("  (No subscriptions yet - this is normal before testing)")

# 4. S3 IMAGES
print("\n S3 IMAGES BUCKET (music-app-images-s4154047):")
resp = s3.list_objects_v2(Bucket='music-app-images-s4154047', Prefix='artist-images/')
images = resp.get('Contents', [])
print(f"  Total images stored: {len(images)}")

# 5. S3 WEBSITE BUCKET
print("\n S3 WEBSITE BUCKET (frontend files):")
resp = s3.list_objects_v2(Bucket='music-app-website-s4154047')
files = resp.get('Contents', [])
for f in files:
    print(f"  {f['Key']}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  Users in DB:        {len(users)}")
print(f"  Songs in DB:        {len(songs)}")
print(f"  Subscriptions:      {len(subs)}")
print(f"  Images in S3:       {len(images)}")
print(f"  Frontend files:     {len(files)}")
print("=" * 60)
