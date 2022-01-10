import os

# cryptography
SECRET_KEY = os.environ['SHARED_SECRET']

# google cloud pub/sub
PROJECT_ID = 'project-pub-task'
TOPIC_ID = 'my-topic'

# slack
SLACK_TOKEN = os.environ['SLACK_TOKEN']