from datetime import datetime
import django
import os
import sys

sys.path.append(os.path.abspath('/home/atti/googleds/dataupload'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "peneszmentesites.settings")
django.setup()
from backend.models import Logs  # noqa


def log(log_value, status="SUCCESS", script_name="sm_vendor_orders", details=""):
    log = Logs(script_name=script_name,
               time=datetime.now(), status=status, value=log_value, details=details)
    log.save()
