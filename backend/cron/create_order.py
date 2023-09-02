from ..utils.logs import log
from ..utils.minicrm import get_all_adatlap_details, create_order
from ..models import FelmeresItems, Offers, Products
import os
import dotenv
dotenv.load_dotenv()
import requests

def main():
    log("Megrendelések létrehozása elkezdődött", script_name="pen_create_order", status="INFO")
    adatlapok = get_all_adatlap_details(category_id=21, status_id=2896)
    for adatlap in adatlapok:
        log(f"{adatlap['Name']} megrendelés létrehozása", script_name="pen_create_order", status="INFO")
        id = adatlap["Felmeresid"]
        items = [{"sku": Products.objects.filter(id=i.productId)[0].sku if Products.objects.filter(id=i.productId).exists() else "", "productId": i.productId, "netPrice": i.netPrice, "inputValues": i.inputValues, "name": i.name} for i in FelmeresItems.objects.filter(adatlap_id=id)]
        offer = Offers.objects.filter(adatlap_id=adatlap["Id"])
        if offer:
            order = create_order(adatlap_id=id, contact_id=adatlap["ContactId"], items=items, offer_id=offer[0].offer_id, adatlap_status="Szervezésre vár")
            if order == "Error":
                log(f"{adatlap['Name']} megrendelés létrehozása sikertelen", script_name="pen_create_order", status="ERROR")
                continue
            log(f"{adatlap['Name']} megrendelés létrehozása sikeres", script_name="pen_create_order", status="SUCCESS")
            system_id = os.environ.get("PEN_MINICRM_SYSTEM_ID")
            api_key = os.environ.get("PEN_MINICRM_API_KEY")
            requests.post(
                f'https://r3.minicrm.hu/Api/Offer/{offer[0].offer_id}/Project', auth=(system_id, api_key), json={"StatusId": "Sikeres megrendelés"})
            continue
        log(f"{adatlap['Name']} megrendelés létrehozása sikertelen, nem létezik felmérés", script_name="pen_create_order", status="ERROR")
    log("Megrendelések létrehozása sikeresen befejeződött", script_name="pen_create_order", status="SUCCESS")
main()