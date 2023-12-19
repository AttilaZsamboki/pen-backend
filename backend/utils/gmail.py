import os
import pickle
from base64 import urlsafe_b64encode
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build


def gmail_authenticate():
    if os.path.exists(f"backend/utils/token.pickle"):
        with open(f"backend/utils/token.pickle", "rb") as token:
            creds = pickle.load(token)
            return build("gmail", "v1", credentials=creds)
    print("No token.pickle found, please authenticate")


SCOPES = ["https://mail.google.com/"]
our_email = "admin@foliasjuci.hu"


def build_message(destination, obj, body, attachment_path):
    message = MIMEMultipart()
    message["to"] = destination
    message["from"] = our_email
    message["subject"] = obj
    message["body"] = body
    message["reply-to"] = "beszerzes@foliasjuci.hu"
    message.attach(MIMEText(body, "plain"))

    # Add body to email
    if attachment_path != "":
        # Add attachment
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename=attachment.xlsx",
            )
            message.attach(part)

    return {"raw": urlsafe_b64encode(message.as_bytes()).decode()}


def send_email(service, destination, obj, body, attachment=""):
    return (
        service.users()
        .messages()
        .send(
            userId="me",
            body=build_message(destination, obj, body, attachment_path=attachment),
        )
        .execute()
    )
