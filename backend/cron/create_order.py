from ..utils.logs import log
from ..utils.minicrm import get_all_adatlap_details, create_order, get_adatlap_details

from ..models import FelmeresItems, Offers, Felmeresek

import os
import dotenv
import requests
import traceback

dotenv.load_dotenv()


def main():
    log(
        "Megrendelések létrehozása elkezdődött",
        script_name="pen_create_order",
        status="INFO",
    )
    adatlapok = get_all_adatlap_details(category_id=21, status_id=2896)
    for adatlap in adatlapok:
        log(
            f"{adatlap['Name']} megrendelés létrehozása",
            script_name="pen_create_order",
            status="INFO",
        )
        id = adatlap["Felmeresid"]
        adatlap_id = Felmeresek.objects.get(id=id).adatlap_id
        items = [
            {
                "sku": i.product.sku if i.product else "",
                "product_id": i.product.id if i.product else "",
                "netPrice": i.netPrice,
                "inputValues": i.inputValues,
                "name": i.name if i.name else i.product.name,
            }
            for i in FelmeresItems.objects.filter(adatlap_id=id)
        ]
        offer = Offers.objects.filter(adatlap=adatlap["Id"])
        felmeres = get_adatlap_details(adatlap_id)
        if offer and items and felmeres["status"] != "Error":
            felmeres = felmeres["response"]
            order = create_order(
                adatlap_id=adatlap_id,
                contact_id=adatlap["ContactId"],
                items=items,
                offer_id=offer[0].offer_id,
                adatlap_status="Szervezésre vár",
                project_data={
                    "Megye2": felmeres["Megye"],
                    "Utcakep": felmeres["StreetViewUrl"],
                    "IngatlanKepe2": felmeres["IngatlanKepe"],
                    "FelmeresLink": felmeres["FelmeresAdatok"],
                    "KiMerteFel2": felmeres["Felmero2"],
                    "FelmeresDatuma2": felmeres["FelmeresIdopontja2"],
                },
            )
            if order["status"] == "error":
                if order["response"].lower() == "xml is not valid!":
                    log(
                        f"{adatlap['Name']} megrendelés létrehozása sikertelen, XML nem valid",
                        script_name="pen_create_order",
                        status="ERROR",
                        details=order["xml"],
                    )
                    continue
                elif order["response"].lower() == "input doesn't look like it's an xml":
                    log(
                        f"{adatlap['Name']} megrendelés létrehozása sikertelen, input nem XML",
                        script_name="pen_create_order",
                        status="ERROR",
                        details=order["xml"],
                    )
                    continue
                log(
                    f"{adatlap['Name']} megrendelés létrehozása sikertelen",
                    script_name="pen_create_order",
                    status="ERROR",
                    details=order["response"],
                )
                continue
            system_id = os.environ.get("PEN_MINICRM_SYSTEM_ID")
            api_key = os.environ.get("PEN_MINICRM_API_KEY")
            resp = requests.post(
                f"https://r3.minicrm.hu/Api/Offer/{offer[0].offer_id}/Project",
                auth=(system_id, api_key),
                json={"StatusId": "Sikeres megrendelés"},
            )
            if resp.status_code != 200:
                log(
                    f"{adatlap['Name']} megrendelés létrehozása sikertelen, megrendelés státusz frissítése sikertelen",
                    script_name="pen_create_order",
                    status="ERROR",
                    details=resp.text,
                )
                continue
            log(
                f"{adatlap['Name']} megrendelés létrehozása sikeres",
                script_name="pen_create_order",
                status="SUCCESS",
            )
            continue
        log(
            f"{adatlap['Name']} megrendelés létrehozása sikertelen, nem létezik felmérés",
            script_name="pen_create_order",
            status="ERROR",
            details=f"Offer: {offer}. Felmérés: {felmeres}",
        )
    log(
        "Megrendelések létrehozása sikeresen befejeződött",
        script_name="pen_create_order",
        status="SUCCESS",
    )


try:
    main()
except Exception as e:
    log(
        "Megrendelések létrehozása sikertelen",
        script_name="pen_create_order",
        status="ERROR",
        details=f"Error: {e}. {traceback.format_exc()}",
    )
