from ..utils.minicrm import get_all_adatlap, get_adatlap_details
from ..utils.logs import log
from ..models import MiniCrmAdatlapok

adatlapok = get_all_adatlap(29, "3008")
if not adatlapok:
    log(
        "Hiba akadt az adatlapok lekérdezésében",
        "INFO",
        "pen_order_webhook_chceck",
        adatlapok["message"],
    )
db_adatlapok = MiniCrmAdatlapok.objects.filter(
    CategoryId="29", Id__in=[adatlap["Id"] for adatlap in adatlapok]
).exclude(StatusId="3008")
for adatlap in db_adatlapok:
    adatlap = get_adatlap_details(adatlap.Id)
    if adatlap["status"] == "Error":
        log(
            "Hiba akadt az adatlap lekérdezésében",
            "INFO",
            "pen_order_webhook_chceck",
            adatlap["message"],
        )
        continue
    adatlap = adatlap["response"]
    valid_fields = {f.name for f in MiniCrmAdatlapok._meta.get_fields()}
    filtered_data = {
        k: v
        for k, v in adatlap.items()
        if k in valid_fields
        and k
        not in [
            "BusinessId",
            "ProjectHash",
            "ProjectEmail",
            "UserId",
            "CreatedBy",
            "UpdatedBy",
            "LezarasOka",
            "MiertMentunkKiFeleslegesen",
            "ElutasitasOka",
        ]
    }
    MiniCrmAdatlapok(
        StatusId=[i["StatusId"] for i in adatlapok if i["Id"] == adatlap["Id"]][0],
        **filtered_data
    ).save()
