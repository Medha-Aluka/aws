# Music Subscription App  Setup & Run Guide

A cloud-based music subscription web app built on AWS.
Built by: Medha Aluka (s4154047) :RMIT University

---

## Website URL (Just Open This!)

```
http://music-app-website-s4154047.s3-website-us-east-1.amazonaws.com/login.html
```

> **Note:** The AWS Lab must be running (green dot) for the app to work.

---

## Test Login Credentials

| Email | Password | Username |
|-------|----------|----------|
| s41540470@student.rmit.edu.au | 012345 | MedhaAluka0 |
| s41540471@student.rmit.edu.au | 123456 | MedhaAluka1 |
| s41540472@student.rmit.edu.au | 234567 | MedhaAluka2 |
| s41540473@student.rmit.edu.au | 345678 | MedhaAluka3 |
| s41540474@student.rmit.edu.au | 456789 | MedhaAluka4 |

Or register your own account on the Register page.

---

## AWS Backend URLs

| Backend | Technology | URL |
|---------|-----------|-----|
| Backend 1 | API Gateway + Lambda | https://igximhopah.execute-api.us-east-1.amazonaws.com/prod |
| Backend 2 | EC2 + Flask | http://204.236.247.209 |
| Backend 3 | ECS + Docker | http://54.161.95.15 |

---

## How to Start the App (Every Time)

### Step 1 : Start the AWS Lab
1. Go to: https://rmit.instructure.com → AWS Academy
2. Click **"Start Lab"**
3. Wait for the **green dot** next to AWS
4. The website URL above will now work

### Step 2 : Update AWS Credentials (on your PC)
1. In the AWS Academy lab page, click **"AWS Details"**
2. Click **"Show"** next to AWS CLI
3. Copy all 3 lines (aws_access_key_id, aws_secret_access_key, aws_session_token)
4. Open this file on your PC:
   ```
   C:\Users\YOUR_NAME\.aws\credentials
   ```
5. Replace the contents with the copied credentials
6. Save the file

> Credentials expire every 4 hours. Repeat this step each new lab session.

### Step 3 : Restart EC2 Flask Backend (if needed)
1. Go to AWS Console → EC2 → Instances
2. Click on **music-backend-ec2**
3. Click **"Connect"** → **"EC2 Instance Connect"** → **"Connect"**
4. In the black terminal, type:
   ```
   nohup sudo python3 app.py > flask.log 2>&1 &
   ```
5. Press Enter — Flask is now running in background

> ECS backend restarts automatically. Lambda+API Gateway is always on.

---

## Prerequisites (First Time Setup Only)

### Install Python
1. Download Python 3.12: https://www.python.org/downloads/
2. During install, check **"Add Python to PATH"**
3. Verify: open Command Prompt and type `python --version`

### Install AWS CLI
1. Download: https://aws.amazon.com/cli/
2. Run the installer (AWSCLIV2.msi)
3. Verify: open Command Prompt and type `aws --version`

### Install Python packages
Open Command Prompt and run:
```
pip install boto3 flask flask-cors requests
```

### Configure AWS credentials
Open Command Prompt and run:
```
aws configure
```
Enter:
- AWS Access Key ID: (from lab)
- AWS Secret Access Key: (from lab)
- Default region: `us-east-1`
- Default output format: `json`

---

## Project Structure

```
music-app/
├── frontend/
│   ├── login.html        ← Login page
│   ├── register.html     ← Register page
│   └── main.html         ← Main app page
├── backend/
│   ├── app.py            ← Flask app (EC2 + ECS)
│   ├── requirements.txt  ← Python dependencies
│   └── Dockerfile        ← Docker config for ECS
├── lambda/
│   ├── login.py          ← Login Lambda function
│   ├── register.py       ← Register Lambda function
│   ├── query_songs.py    ← Search songs Lambda
│   ├── get_subscriptions.py
│   ├── subscribe.py
│   └── unsubscribe.py
└── setup/
    ├── create_tables.py      ← Creates DynamoDB tables
    ├── load_songs.py         ← Loads 137 songs into DynamoDB
    ├── upload_images.py      ← Uploads artist images to S3
    ├── deploy_lambda.py      ← Deploys all Lambda functions
    ├── deploy_api_gateway.py ← Creates API Gateway
    ├── deploy_frontend.py    ← Uploads frontend to S3
    ├── deploy_ecr.py         ← Builds and pushes Docker image
    ├── deploy_ecs.py         ← Deploys ECS Fargate service
    └── check_aws_data.py     ← Check what's stored in AWS
```

---

##  How to Test the App

### Test 1 : Login
- Open the website URL
- Enter email and password from the table above
- Click Login
- Should redirect to main page showing your username

### Test 2 : Search for Music
- In the **Artist** field type: `Taylor Swift`
- Click **Query**
- Should show songs with album art images

### Test 3 : Subscribe to a Song
- Click the green **Subscribe** button on any song
- Song appears in "Your Subscriptions" section

### Test 4 : Remove a Subscription
- Click the red **Remove** button next to a subscribed song
- Song disappears from subscriptions

### Test 5 : Register New User
- Click "Register here" on login page
- Enter email, username, password
- Success message then redirects to login

### Test 6 : Wrong Password
- Try logging in with incorrect password
- Should show "email or password is invalid"

---

## Check Data in AWS

### Option 1 : AWS Console (visual)
1. Go to: https://us-east-1.console.aws.amazon.com/dynamodbv2/home?region=us-east-1#tables
2. Click on any table (login / music / subscriptions)
3. Click **"Explore table items"** → Click **"Run"**

### Option 2 : Python script
```
cd "C:\orginal documents\project final\aws\music-app\setup"
python check_aws_data.py
```
Shows: all users, songs count, subscriptions, S3 images.

---

## Full Redeployment (If Starting Fresh)

Run these scripts in order from Command Prompt:
```
cd "C:\orginal documents\project final\aws\music-app\setup"

python create_tables.py
python load_songs.py
python upload_images.py
python deploy_lambda.py
python deploy_api_gateway.py
python deploy_frontend.py
python deploy_ecr.py
python deploy_ecs.py
```

> Only needed if tables/functions are deleted. Normally you just start the lab and go!

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Website not loading | Start the AWS Lab (green dot) |
| Login not working | Check email is correct (case-sensitive) |
| Search shows no results | Make sure to type in **Artist** field, not Title |
| EC2 not responding | Reconnect via EC2 Instance Connect and run Flask again |
| Credentials error | Update ~/.aws/credentials from AWS Details panel |
| Songs not loading | Check lab is running and credentials are fresh |

---

##  AWS Services Used

| Service | Purpose |
|---------|---------|
| Amazon S3 | Frontend hosting + artist image storage |
| Amazon DynamoDB | Database (login, music, subscriptions tables) |
| AWS Lambda | Serverless backend functions |
| Amazon API Gateway | REST API routing to Lambda |
| Amazon EC2 | Virtual server running Flask |
| Amazon ECS (Fargate) | Containerised Flask app via Docker |
| Amazon ECR | Docker image registry |

---

*RMIT University — Cloud Computing Assignment 2 — 2026*
