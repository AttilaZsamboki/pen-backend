from ..utils.logs import log
from ..utils.minicrm import update_adatlap_fields

from datetime import datetime


def mini_crm_proxy(request_data, adatlap_id, retry=False):
    log(
        "MiniCRM adatlap frissítése meghívva",
        "INFO",
        "pen_mini_crm_proxy",
        request_data,
    )
    data = update_adatlap_fields(
        id=adatlap_id,
        fields=request_data,
        script_name="pen_mini_crm_proxy",
    )
    if data["code"] == 200:
        log("MiniCRM adatlap frissítése sikeres", "SUCCESS", "pen_mini_crm_proxy")
    else:
        log(
            "MiniCRM adatlap frissítése sikertelen",
            "ERROR",
            "pen_mini_crm_proxy",
            details=data["reason"],
            data={"request_data": request_data, "adatlap_id": adatlap_id},
            retry=retry,
        )

    return data


def cron():
    from ..models import ScriptRetries

    retries = ScriptRetries.objects.all()
    for retry in retries:
        if retry.time < datetime.now():
            log(
                "Újra próbálkozás",
                "INFO",
                "pen_mini_crm_proxy",
                data=retry.log.data,
            )
            globals()[retry.log.script_name.split("pen_")[-1]](**retry.log.data)
            retry.delete()
