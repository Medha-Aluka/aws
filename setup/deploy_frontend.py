import boto3
import json
import os

REGION          = 'us-east-1'
WEBSITE_BUCKET  = 'music-app-website-s4154047'
FRONTEND_DIR    = os.path.join(os.path.dirname(__file__), '../frontend')

s3 = boto3.client('s3', region_name=REGION)

# Step 1: Create website bucket
print(f"Creating website bucket: {WEBSITE_BUCKET}")
try:
    s3.create_bucket(Bucket=WEBSITE_BUCKET)
    print("  Bucket created!")
except Exception as e:
    print(f"  Bucket already exists: {e}")

# Step 2: Disable block public access (needed for static website) ──
s3.put_public_access_block(
    Bucket=WEBSITE_BUCKET,
    PublicAccessBlockConfiguration={
        'BlockPublicAcls':       False,
        'IgnorePublicAcls':      False,
        'BlockPublicPolicy':     False,
        'RestrictPublicBuckets': False
    }
)

# Step 3: Add bucket policy to allow public read 
policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect":    "Allow",
        "Principal": "*",
        "Action":    "s3:GetObject",
        "Resource":  f"arn:aws:s3:::{WEBSITE_BUCKET}/*"
    }]
}
s3.put_bucket_policy(
    Bucket=WEBSITE_BUCKET,
    Policy=json.dumps(policy)
)
print("  Public read policy applied!")

# Step 4: Enable static website hosting
s3.put_bucket_website(
    Bucket=WEBSITE_BUCKET,
    WebsiteConfiguration={
        'IndexDocument': {'Suffix': 'login.html'},
        'ErrorDocument': {'Key':    'login.html'}
    }
)
print("  Static website hosting enabled!")

#Step 5: Upload all HTML files
print("\nUploading HTML files...")
html_files = ['login.html', 'register.html', 'main.html']
for filename in html_files:
    filepath = os.path.join(FRONTEND_DIR, filename)
    s3.upload_file(
        filepath, WEBSITE_BUCKET, filename,
        ExtraArgs={'ContentType': 'text/html'}
    )
    print(f"  Uploaded: {filename}")

website_url = f"http://{WEBSITE_BUCKET}.s3-website-{REGION}.amazonaws.com"
print(f"\n{'='*60}")
print(f"FRONTEND IS LIVE!")
print(f"Website URL:")
print(f"{website_url}")
print(f"{'='*60}")
print(f"\nOpen this in your browser to test your app:")
print(f"{website_url}/login.html")
