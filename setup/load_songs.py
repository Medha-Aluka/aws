import boto3
import json
import os

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('music')

# Path to the songs file to adjust if needed
songs_file = r'C:\orginal documents\project final\aws\2026a2_songs.json'

with open(songs_file, 'r') as f:
    data = json.load(f)

songs = data['songs']
print(f"Found {len(songs)} songs to load...")

# batch_writer it automatically groups items into batches of 25 (DynamoDB limit)
# and handles retries this is the correct way to bulk-load data
with table.batch_writer() as batch:
    for i, song in enumerate(songs):
        item = {
            'artist':    song['artist'],
            'song_key':  f"{song['title']}#{song['album']}",  # e.g. "Delicate#Reputation"
            'title':     song['title'],
            'year':      song['year'],
            'album':     song['album'],
            'image_url': song['img_url']
        }
        batch.put_item(Item=item)
        if (i + 1) % 20 == 0:
            print(f"  Loaded {i + 1}/{len(songs)} songs...")

print(f"\nAll songs loaded! Verifying...")

# Verifies the count matches if not, key schema has overwrites
response = table.scan(Select='COUNT')
count = response['Count']
print(f"Songs in DynamoDB: {count}")
print(f"Songs in JSON file: {len(songs)}")

if count == len(songs):
    print("SUCCESS - All songs loaded with zero overwrites!")
else:
    print(f"WARNING - {len(songs) - count} songs were overwritten. Check key schema!")
