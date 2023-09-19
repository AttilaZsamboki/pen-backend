from ..utils.logs import log
from ..utils.minicrm import get_all_adatlap_details, create_order, get_adatlap_details

from ..models import FelmeresItems, Offers, Products, Felmeresek

import os
import dotenv
import requests

dotenv.load_dotenv()

def main():
    log("Megrendelések létrehozása elkezdődött", script_name="pen_create_order", status="INFO")
    adatlapok = get_all_adatlap_details(category_id=21, status_id=2896)
    for adatlap in adatlapok:
        log(f"{adatlap['Name']} megrendelés létrehozása", script_name="pen_create_order", status="INFO")
        id = Felmeresek.objects.filter(adatlap_id=adatlap["Felmeresid"]).order_by("-created_at")[0].id
        items = [{"sku": Products.objects.filter(id=i.productId)[0].sku if Products.objects.filter(id=i.productId).exists() else "", "productId": i.productId, "netPrice": i.netPrice, "inputValues": i.inputValues, "name": i.name} for i in FelmeresItems.objects.filter(adatlap_id=id)]
        offer = Offers.objects.filter(adatlap_id=adatlap["Id"])
        felmeres = get_adatlap_details(adatlap["Felmeresid"])
        if offer and items and felmeres["status"] != "Error":
            felmeres = felmeres["response"]
            order = create_order(adatlap_id=adatlap["Felmeresid"], contact_id=adatlap["ContactId"], items=items, offer_id=offer[0].offer_id, adatlap_status="Szervezésre vár", project_data={"Megye2": felmeres["Megye"], "Utcakep": felmeres["StreetViewUrl"], "IngatlanKepe2": felmeres["IngatlanKepe"], "FelmeresLink": felmeres["FelmeresAdatok"], "KiMerteFel2": felmeres["Felmero2"],"FelmeresDatuma2": felmeres["FelmeresIdopontja2"] })
            if order["status"] == "error":
                if order["response"].lower() == "xml is not valid!":
                    log(f"{adatlap['Name']} megrendelés létrehozása sikertelen, XML nem valid", script_name="pen_create_order", status="ERROR", details=order["xml"])
                    continue
                elif order["response"].lower() == "input doesn't look like it's an xml":
                    log(f"{adatlap['Name']} megrendelés létrehozása sikertelen, input nem XML", script_name="pen_create_order", status="ERROR", details=order["xml"])
                    continue
                log(f"{adatlap['Name']} megrendelés létrehozása sikertelen", script_name="pen_create_order", status="ERROR", details=order["response"])
                continue
            log(f"{adatlap['Name']} megrendelés létrehozása sikeres", script_name="pen_create_order", status="SUCCESS")
            system_id = os.environ.get("PEN_MINICRM_SYSTEM_ID")
            api_key = os.environ.get("PEN_MINICRM_API_KEY")
            requests.post(
                f'https://r3.minicrm.hu/Api/Offer/{offer[0].offer_id}/Project', auth=(system_id, api_key), json={"StatusId": "Sikeres megrendelés"})
            continue
        log(f"{adatlap['Name']} megrendelés létrehozása sikertelen, nem létezik felmérés", script_name="pen_create_order", status="ERROR", details=f"Felmérés: {felmeres}")
    log("Megrendelések létrehozása sikeresen befejeződött", script_name="pen_create_order", status="SUCCESS")
main()