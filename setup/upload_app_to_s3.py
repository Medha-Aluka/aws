import boto3
import os

REGION      = 'us-east-1'
BUCKET_NAME = 'music-app-images-s4154047'
APP_PATH    = os.path.join(os.path.dirname(__file__), '../backend/app.py')

s3 = boto3.client('s3', region_name=REGION)

print("Uploading app.py to S3...")
s3.upload_file(APP_PATH, BUCKET_NAME, 'app.py')
print(f"Done! app.py is now at s3://{BUCKET_NAME}/app.py")
print()
print("="*60)
print("Now in your EC2 terminal, run these 4 commands:")
print("="*60)
print()
print("1)  sudo dnf install python3-pip -y")
print()
print("2)  pip3 install flask flask-cors boto3")
print()
print("3)  aws s3 cp s3://music-app-images-s4154047/app.py ~/app.py")
print()
print("4)  sudo python3 ~/app.py")
print()
print("="*60)
print("When you see '* Running on http://0.0.0.0:80' — it's working!")
print("="*60)
