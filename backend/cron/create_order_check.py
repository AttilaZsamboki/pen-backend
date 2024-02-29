from .create_order import create_order
from ..utils.logs import log
from ..utils.minicrm import get_all_adatlap
from ..models import MiniCrmAdatlapok

log("Megrendelés ellenőrzés indítása...", "INFO", "pen_create_order_check")
adatlapok = get_all_adatlap(21, 2896)
for adatlap in adatlapok:
    log(
        "Megrendelés nem jött létre",
        "INFO",
        "pen_create_order_check",
        str(adatlap["Id"]),
    )
    adatlap = MiniCrmAdatlapok.objects.get(id=adatlap["Id"])
    create_order(adatlap)
