from ..services.minicrm import MiniCRMWrapper
from ..models import Order, Systems
from django.db.models import Q


class Main(MiniCRMWrapper):
    script_name = "pen_erp_status_sync"

    def main(self):
        self.log("MiniCRM ERP státusz szinkron megkezdődött", "INFO")
        adatlapok = self.get_adatlapok(
            ~Q(StatusIdStr="Sikeres")
            & ~Q(Enum1951="Lezárva")
            & ~Q(Enum1951="Szervezésre vár")
            & ~Q(StatusId="Sikertelen"),
            CategoryId="Megrendelés",
            Deleted=0,
        )
        if not adatlapok:
            self.log("Nincs új adatlap a MiniCRM-ben", "INFO")
            return
        if adatlapok == "Error":
            self.log("Hiba történt a MiniCRM API hívás során", "ERROR")
            return

        for adatlap in adatlapok:
            try:
                order = Order.objects.get(
                    webshop_id=self.get_orders(adatlap_id=adatlap.Id).order_id
                )
            except Order.DoesNotExist:
                self.log(
                    "Nem található megfelelő rendelés",
                    "WARNING",
                    details=adatlap.Id,
                )
                continue
            if (
                order.order_status == "Completed"
                and adatlap.StatusIdStr == "Folyamatban"
            ):
                resp2 = self.minicrm_client.update_offer_order(
                    order.webshop_id, {"Enum1951": "Elszámolásra vár"}, type="Order"
                )
                resp = self.minicrm_client.update_order_status(order.webshop_id)
                if not resp.ok or not resp2.status_code != 200:
                    self.log(
                        "Hiba történt a MiniCRM API hívás során",
                        "FAILED",
                        details=f"OrderId: {order.order_id}. Response: {resp.text}",
                    )
                    continue
            elif order.payment_status == "Completed":
                resp2 = self.minicrm_client.update_offer_order(
                    order.webshop_id, {"Enum1951": "Lezárva"}, type="Order"
                )
                resp = self.minicrm_client.update_order_status(order.webshop_id, "Paid")
                if not resp.ok or not resp2.status_code != 200:
                    self.log(
                        "Hiba történt a MiniCRM API hívás során",
                        "FAILED",
                        details=f"OrderId: {order.order_id}. Response: {resp.text}",
                    )
                    continue

            self.log(
                "MiniCRM ERP státusz szinkron sikeresen lefutott",
                "INFO",
                details=adatlap["Id"],
            )


for system in Systems.objects.all():
    Main(system=system).main()
