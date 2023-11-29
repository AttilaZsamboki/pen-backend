from datetime import datetime, timedelta
import django
import os
import sys

sys.path.append(os.path.abspath("/home/atti/googleds/dataupload"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "peneszmentesites.settings")
django.setup()
from backend.models import Logs, MiniCrmRequests, ScriptRetries  # noqa


def log(
    log_value,
    status="SUCCESS",
    script_name="sm_vendor_orders",
    details="",
    data={},
    retry=False,
):
    log = Logs(
        script_name=script_name,
        time=datetime.now(),
        status=status,
        value=log_value,
        details=details,
        data=data,
    )
    log.save()
    if retry:
        for i in range(5):
            time = 0
            match i:
                case 0:
                    time = 5
                case 1:
                    time = 10
                case 2:
                    time = 30
                case 3:
                    time = 60
                case 4:
                    time = 120
            ScriptRetries(log=log, time=datetime.now() + timedelta(minutes=time)).save()


def log_minicrm_request(endpoint, script, description=None):
    MiniCrmRequests(
        time=datetime.now(),
        endpoint=endpoint,
        script=script,
        description=description,
    ).save()
