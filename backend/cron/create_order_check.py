from .create_order import create_order
from ..utils.logs import log
from ..utils.minicrm import MiniCrmClient
from ..models import MiniCrmAdatlapok

log("Megrendelés ellenőrzés indítása...", "INFO", "pen_create_order_check")
minicrm_client = MiniCrmClient(script_name="pen_create_order_check")
adatlapok = minicrm_client.get_all_adatlap(21, 2896)
for adatlap in adatlapok:
    log(
        "Megrendelés nem jött létre",
        "INFO",
        "pen_create_order_check",
        str(adatlap["Id"]),
    )
    adatlap = MiniCrmAdatlapok.objects.get(id=adatlap["Id"])
    create_order(adatlap)
