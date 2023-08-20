from ..config_development import base_path as dev
from ..config_production import base_path as prod
import boto3
from django.conf import settings
from dotenv import load_dotenv
import os
load_dotenv()

base_path = dev if os.environ.get("ENVIRONMENT") == "development" else prod

def delete_s3_file(file_path):
    s3_client = boto3.client('s3', aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"), region_name=os.environ.get("AWS_REGION"))
    s3_client.delete_object(Bucket=os.environ.get("AWS_BUCKET_NAME"), Key=file_path)