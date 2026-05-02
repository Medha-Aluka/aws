import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
client = boto3.client('dynamodb', region_name='us-east-1')

# ──────────────────────────────────────────────────────────
# TABLE 1: LOGIN TABLE
# Primary Key: for email (each user has a unique email)
# ──────────────────────────────────────────────────────────
print("Creating login table...")
try:
    login_table = dynamodb.create_table(
        TableName='login',
        KeySchema=[
            {'AttributeName': 'email', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'email', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    login_table.wait_until_exists()
    print("Login table created!\n")
except Exception as e:
    print(f"Login table already exists or error: {e}\n")

# Login table data using our student ID (s4154047) and my name (Medha Aluka)
# Pattern: email = studentID + number + @student.rmit.edu.au
# username = FirstnameLastname + number
# password = 012345, 123456, 234567, 345678, 456789, 567890, 678901, 789012, 890123, 901234
login_table = dynamodb.Table('login')
users = [
    {"email": "s41540470@student.rmit.edu.au", "user_name": "MedhaAluka0", "password": "012345"},
    {"email": "s41540471@student.rmit.edu.au", "user_name": "MedhaAluka1", "password": "123456"},
    {"email": "s41540472@student.rmit.edu.au", "user_name": "MedhaAluka2", "password": "234567"},
    {"email": "s41540473@student.rmit.edu.au", "user_name": "MedhaAluka3", "password": "345678"},
    {"email": "s41540474@student.rmit.edu.au", "user_name": "MedhaAluka4", "password": "456789"},
    {"email": "s41540475@student.rmit.edu.au", "user_name": "MedhaAluka5", "password": "567890"},
    {"email": "s41540476@student.rmit.edu.au", "user_name": "MedhaAluka6", "password": "678901"},
    {"email": "s41540477@student.rmit.edu.au", "user_name": "MedhaAluka7", "password": "789012"},
    {"email": "s41540478@student.rmit.edu.au", "user_name": "MedhaAluka8", "password": "890123"},
    {"email": "s41540479@student.rmit.edu.au", "user_name": "MedhaAluka9", "password": "901234"},
]
for user in users:
    login_table.put_item(Item=user)
    print(f"  Added user: {user['email']}")
print("All 10 users added!\n")

# ──────────────────────────────────────────────────────────
# TABLE 2: MUSIC TABLE
#
# INDEXES:
#   LSI (artist/year/index): same PK=artist, SK=year
#       → Used for: "Find all songs by Taylor Swift in 2014"
#       → Uses DynamoDB Query (efficient, not Scan)
#
#   GSI (year/artist/index): PK=year, SK=artist
#       → Used for: "Find all songs from 1974"
#       → Uses DynamoDB Query (efficient, not Scan)
# ──────────────────────────────────────────────────────────
print("Creating music table...")
try:
    music_table = dynamodb.create_table(
        TableName='music',
        KeySchema=[
            {'AttributeName': 'artist',   'KeyType': 'HASH'},
            {'AttributeName': 'song_key', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'artist',   'AttributeType': 'S'},
            {'AttributeName': 'song_key', 'AttributeType': 'S'},
            {'AttributeName': 'year',     'AttributeType': 'S'},
        ],
        LocalSecondaryIndexes=[
            {
                'IndexName': 'artist-year-index',
                'KeySchema': [
                    {'AttributeName': 'artist', 'KeyType': 'HASH'},
                    {'AttributeName': 'year',   'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'}
            }
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'year-artist-index',
                'KeySchema': [
                    {'AttributeName': 'year',   'KeyType': 'HASH'},
                    {'AttributeName': 'artist', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'}
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    music_table.wait_until_exists()
    print("Music table created with GSI + LSI!\n")
except Exception as e:
    print(f"Music table already exists or error: {e}\n")

# ──────────────────────────────────────────────────────────
# TABLE 3: SUBSCRIPTIONS TABLE
# Stores which songs each user has subscribed to
# Partition Key = email, Sort Key = song_key
# ──────────────────────────────────────────────────────────
print("Creating subscriptions table...")
try:
    sub_table = dynamodb.create_table(
        TableName='subscriptions',
        KeySchema=[
            {'AttributeName': 'email',    'KeyType': 'HASH'},
            {'AttributeName': 'song_key', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'email',    'AttributeType': 'S'},
            {'AttributeName': 'song_key', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    sub_table.wait_until_exists()
    print("Subscriptions table created!\n")
except Exception as e:
    print(f"Subscriptions table already exists or error: {e}\n")

print("ALL TABLES ARE READY!")
