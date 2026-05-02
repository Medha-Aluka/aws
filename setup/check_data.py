import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('music')

# Scan all songs
resp = table.scan()
items = resp['Items']

# Get unique artists
artists = sorted(set(i['artist'] for i in items))

print(f"Total songs in database: {len(items)}")
print(f"Total unique artists: {len(artists)}")
print("\n--- ALL ARTISTS ---")
for a in artists:
    print(f"  {a}")
