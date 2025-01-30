import base64
from ..config_development import base_path as dev
from ..config_production import base_path as prod
from google.oauth2 import service_account
import json
import boto3
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os
import datetime
from typing import List

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
    print(field_names["ArajanlatMegjegyzes"])
    return {field_names.get(k, k): v for k, v in data.items()}


def filter_fields(model, data):
    return {k: v for k, v in data.items() if k in model._meta.fields}


def get_credentials(scopes: List[str]):
    """Get credentials from environment variable"""
    # Get base64 encoded credentials from environment
    encoded_creds = os.environ.get("GOOGLE_CREDENTIALS")
    if not encoded_creds:
        raise ValueError("GOOGLE_CREDENTIALS environment variable not set")

    # Decode and create temp file
    creds_json = base64.b64decode(encoded_creds)
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(creds_json), scopes=scopes
    )
    return credentials

def get_spreadsheet(sheet_name, worksheet_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = get_credentials(scope)
    client = gspread.authorize(credentials)

    sheet = client.open(sheet_name).worksheet(worksheet_name)
    return sheet


def round_to_closest_hour(dt):
    datetime_min = datetime.datetime.min.replace(tzinfo=dt.tzinfo)
    dt += datetime.timedelta(minutes=30)
    rounded_seconds = (dt - datetime_min).total_seconds() // 3600 * 3600
    return datetime_min + datetime.timedelta(seconds=rounded_seconds)


def get_address(adatlap):
    return (
        f"{adatlap.Cim2} {adatlap.Telepules}, {adatlap.Iranyitoszam} {adatlap.Orszag}"
    )


def round_to_five(n):
    return round(n / 5) * 5


def is_number(n):
    if n is None:
        return False
    try:
        int(n)
        return True
    except ValueError:
        return False


def round_to_30(dt: datetime) -> datetime:
    if dt.minute >= 30:
        return (
            dt.replace(minute=30, second=0)
            if dt.minute < 45
            else dt.replace(hour=(dt.hour + 1) % 24, minute=0, second=0)
        )
    else:
        return (
            dt.replace(minute=0, second=0)
            if dt.minute < 15
            else dt.replace(minute=30, second=0)
        )
