from ..utils.minicrm import MiniCrmClient
from ..utils.logs import log as l
from ..models import Orders, Order, MiniCrmAdatlapok
from functools import partial


def main():
    script_name = "pen_erp_order_id"
    log = partial(l, script_name=script_name)
    minicrm_client = MiniCrmClient(script_name=script_name)

    log("MiniCRM ERP rendelésszám szinkron megkezdődött", "INFO")
    adatlapok = MiniCrmAdatlapok.objects.filter(
        CategoryId=29, ClouderpMegrendeles__isnull=True, RendelesSzama__isnull=True
    )
    for adatlap in adatlapok:
        order_id = Orders.objects.filter(adatlap_id=adatlap.Id).first()
        if not order_id:
            log(
                "Nem található megfelelő rendelés a megrendeléshez",
                "WARNING",
                adatlap.Id,
            )
            continue
        order_id = order_id.order_id

        order = Order.objects.filter(webshop_id=order_id).first()
        if not order:
            log(
                "Nincs benne a rendelés az ERP feedben",
                "WARNING",
                adatlap.Id,
            )
            continue
        resp = minicrm_client.update_offer_order(
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
                order_id,
            )
        else:
            log(
                "Rendelésszám frissítése sikertelen",
                "ERROR",
                f"OrderId: {order_id}. Response: {resp.text}",
            )


main()
