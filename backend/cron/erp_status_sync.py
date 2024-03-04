from ..utils.minicrm import update_order_status, update_offer_order
from ..utils.logs import log
from ..models import Orders, Order, MiniCrmAdatlapok
from django.db.models import Q


def main():
    log("MiniCRM ERP státusz szinkron megkezdődött", "INFO", "pen_erp_status_sync")
    adatlapok = MiniCrmAdatlapok.objects.filter(
        ~Q(StatusId=3009),
        CategoryId=29,
        Enum1951="Beépítésre vár",
        Deleted=0,
    ).values()
    if not adatlapok:
        log("Nincs új adatlap a MiniCRM-ben", "INFO", "pen_erp_status_sync")
        return
    if adatlapok == "Error":
        log("Hiba történt a MiniCRM API hívás során", "ERROR", "pen_erp_status_sync")
        return

    for adatlap in adatlapok:
        try:
            order = Order.objects.get(
                webshop_id=Orders.objects.get(adatlap_id=adatlap["Id"]).order_id
            )
        except Order.DoesNotExist:
            log(
                "Nem található megfelelő rendelés",
                "WARNING",
                "pen_erp_status_sync",
                adatlap["Id"],
            )
            continue
        if order.order_status == "Completed":
            resp2 = update_offer_order(
                order.webshop_id, {"Enum1951": "Lezárva"}, type="Order"
            )
            resp = update_order_status(order.webshop_id)
            if not resp.ok or not resp2["code"] != 200:
                log(
                    "Hiba történt a MiniCRM API hívás során",
                    "FAILED",
                    "pen_erp_status_sync",
                    f"OrderId: {order.order_id}. Response: {resp.text}",
                )
                continue
        if order.payment_status == "Completed":
            resp2 = update_offer_order(
                order.webshop_id, {"Enum1951": "Lezárva"}, type="Order"
            )
            resp = update_order_status(order.webshop_id, "Paid")
            if not resp.ok or not resp2["code"] != 200:
                log(
                    "Hiba történt a MiniCRM API hívás során",
                    "FAILED",
                    "pen_erp_status_sync",
                    f"OrderId: {order.order_id}. Response: {resp.text}",
                )
                continue
        log(
            "MiniCRM ERP státusz szinkron sikeresen lefutott",
            "INFO",
            "pen_erp_status_sync",
            adatlap["Id"],
        )


main()
