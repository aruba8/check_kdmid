import os

bucket_name = os.getenv("BUCKET_NAME")
sender = os.getenv("EMAIL_SENDER")
recipient = os.getenv("EMAIL_RECIPIENT")
region = os.getenv("AWS_REGION")