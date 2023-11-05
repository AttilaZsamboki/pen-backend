from ..utils.minicrm import get_all_adatlap, update_order_status
from ..utils.logs import log
from ..models import Orders, Order


def main():
    log("MiniCRM ERP státusz szinkron megkezdődött", "INFO", "pen_erp_status_sync")
    adatlapok = get_all_adatlap(
        category_id=29, criteria=lambda adatlap: adatlap["StatusId"] in [3008, 3012]
    )
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
                "ERROR",
                "pen_erp_status_sync",
                adatlap["Id"],
            )
            continue
        if adatlap["StatusId"] == 3008 and order.order_status == "Completed":
            resp = update_order_status(order.webshop_id)
            if not resp.ok:
                log(
                    "Hiba történt a MiniCRM API hívás során",
                    "ERROR",
                    "pen_erp_status_sync",
                    f"OrderId: {order.order_id}. Response: {resp.text}",
                )
                continue
        if order.payment_status == "Completed":
            resp = update_order_status(order.webshop_id, "Paid")
            if not resp.ok:
                log(
                    "Hiba történt a MiniCRM API hívás során",
                    "ERROR",
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
