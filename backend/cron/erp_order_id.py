from ..utils.minicrm import update_offer_order
from ..utils.logs import log
from ..models import Orders, Order, MiniCrmAdatlapok


def main():
    log("MiniCRM ERP rendelésszám szinkron megkezdődött", "INFO", "pen_erp_order_id")
    adatlapok = MiniCrmAdatlapok.objects.filter(
        CategoryId=29,
        ClouderpMegrendeles__isnull=True,
        RendelesSzama__isnull=True,
        Deleted="0",
    )
    for adatlap in adatlapok:
        order_id = Orders.objects.filter(adatlap_id=adatlap.Id).first()
        if not order_id:
            log(
                "Nem található megfelelő rendelés a megrendeléshez",
                "WARNING",
                "pen_erp_order_id",
                adatlap.Id,
            )
            continue
        order_id = order_id.order_id

        order = Order.objects.filter(webshop_id=order_id).first()
        if not order:
            log(
                "Nincs benne a rendelés az ERP feedben",
                "WARNING",
                "pen_erp_order_id",
                adatlap.Id,
            )
            continue
        resp = update_offer_order(
            order.webshop_id,
            {
                "ClouderpMegrendeles": "https://app.clouderp.hu/v2/order?search="
                + str(order.order_id),
                "RendelesSzama": order.order_id,
            },
            type="Order",
        )
        if resp.ok:
            log(
                "Rendelésszám sikeresen frissítve",
                "SUCCESS",
                "pen_erp_order_id",
                order_id,
            )
        else:
            log(
                "Rendelésszám frissítése sikertelen",
                "ERROR",
                "pen_erp_order_id",
                f"OrderId: {order_id}. Response: {resp.text}",
            )


main()
