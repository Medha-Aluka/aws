import boto3
import json
import requests
import os

BUCKET_NAME = 'music-app-images-s4154047'
REGION = 'us-east-1'

s3 = boto3.client('s3', region_name=REGION)

# Step 1: Create the S3 bucket
print(f"Creating S3 bucket: {BUCKET_NAME}")
try:
    s3.create_bucket(Bucket=BUCKET_NAME)
    print("Bucket created!\n")
except Exception as e:
    print(f"Bucket already exists or error: {e}\n")

# Step 2: Block all public access (security best practice)
# We need to use presigned URLs to securely access images instead
s3.put_public_access_block(
    Bucket=BUCKET_NAME,
    PublicAccessBlockConfiguration={
        'BlockPublicAcls': True,
        'IgnorePublicAcls': True,
        'BlockPublicPolicy': True,
        'RestrictPublicBuckets': True
    }
)
print("Public access blocked (using presigned URLs for secure access)\n")

# Step 3: Loads songs JSON to get all image URLs
songs_file = r'C:\orginal documents\project final\aws\2026a2_songs.json'
with open(songs_file, 'r') as f:
    data = json.load(f)

# Gets unique image URLs only (71 unique artists = 71 images)
unique_urls = {}
for song in data['songs']:
    filename = song['img_url'].split('/')[-1]  # e.g. "TaylorSwift.jpg"
    unique_urls[filename] = song['img_url']

print(f"Found {len(unique_urls)} unique artist images to download and upload...\n")

# Step 4: Download each image and upload to S3
success = 0
failed = 0
for filename, url in unique_urls.items():
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=f'artist-images/{filename}',
                Body=response.content,
                ContentType='image/jpeg'
            )
            print(f"  Uploaded: {filename}")
            success += 1
        else:
            print(f"  FAILED to download: {url}")
            failed += 1
    except Exception as e:
        print(f"  ERROR with {filename}: {e}")
        failed += 1

print(f"\nDone! {success} images uploaded, {failed} failed.")
print(f"\nYour bucket name is: {BUCKET_NAME}")
print("SAVE THIS - you will need it in app.py and Lambda functions!")
