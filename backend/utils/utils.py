from ..config_development import base_path as dev
from ..config_production import base_path as prod
import boto3
from dotenv import load_dotenv

import os

load_dotenv()

base_path = dev if os.environ.get("ENVIRONMENT") == "development" else prod


def delete_s3_file(file_path):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_REGION"),
    )
    s3_client.delete_object(Bucket=os.environ.get("AWS_BUCKET_NAME"), Key=file_path)


def replace_self_closing_tags(match):
    self_closing_tags = ["br", "img", "input", "hr", "meta", "link"]
    tag = match.group(1)
    if tag in self_closing_tags:
        return "<{}{}/>".format(tag, match.group(2))
    else:
        return match.group(0)


def map_db_column_to_field(model, data):
    field_names = {
        f.db_column: f.name for f in model._meta.fields if f.db_column is not None
    }
    return {field_names.get(k, k): v for k, v in data.items()}
