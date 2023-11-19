from ..utils.logs import log
from ..utils.minicrm import create_order, get_adatlap_details
from ..utils.minicrm_str_to_text import warranty_type_map

from ..models import Offers, Felmeresek, MiniCrmAdatlapok

import os
import dotenv
import requests
import traceback

dotenv.load_dotenv()


def main(adatlap):
    log(
        "Megrendelések létrehozása elkezdődött",
        script_name="pen_create_order",
        status="INFO",
    )

    try:
        log(
            f"{adatlap['Name']} megrendelés létrehozása",
            script_name="pen_create_order",
            status="INFO",
        )
    except Exception as e:
        log(
            f"Adatlap nevének lekérése sikertelen, Error: {e}",
            script_name="pen_create_order",
            status="ERROR",
            details=f"Adatlap: {adatlap}",
        )
    id = adatlap["Felmeresid"]
    felmeres = Felmeresek.objects.get(id=id)
    offer = Offers.objects.filter(projectid=adatlap["Id"]).first()
    adatlap_details = get_adatlap_details(felmeres.adatlap_id)
    if offer and adatlap_details["status"] != "Error":
        adatlap_details = adatlap_details["response"]
        order = create_order(
            adatlap_id=felmeres.adatlap_id,
            contact_id=adatlap["ContactId"],
            offer_id=offer.id,
            adatlap_status="Szervezésre vár",
            project_data={
                "Megye2": adatlap_details["Megye"],
                "Utcakep": adatlap_details["StreetViewUrl"],
                "IngatlanKepe2": adatlap_details["IngatlanKepe"],
                "FelmeresLink": adatlap_details["FelmeresAdatok"],
                "KiMerteFel2": adatlap_details["Felmero2"],
                "FelmeresDatuma2": adatlap_details["FelmeresIdopontja2"],
                "GaranciaTipusa": warranty_type_map[felmeres.warranty],
                "Indoklas": felmeres.warranty_reason,
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
                return
            elif order["response"].lower() == "input doesn't look like it's an xml":
                log(
                    f"{adatlap['Name']} megrendelés létrehozása sikertelen, input nem XML",
                    script_name="pen_create_order",
                    status="ERROR",
                    details=order["xml"],
                )
                return
            log(
                f"{adatlap['Name']} megrendelés létrehozása sikertelen",
                script_name="pen_create_order",
                status="ERROR",
                details=order["response"],
            )
            return
        system_id = os.environ.get("PEN_MINICRM_SYSTEM_ID")
        api_key = os.environ.get("PEN_MINICRM_API_KEY")
        resp = requests.post(
            f"https://r3.minicrm.hu/Api/Offer/{offer.id}/Project",
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
            return
        log(
            f"{adatlap['Name']} megrendelés létrehozása sikeres",
            script_name="pen_create_order",
            status="SUCCESS",
        )
        return
    log(
        f"{adatlap['Name']} megrendelés létrehozása sikertelen, nem létezik felmérés",
        script_name="pen_create_order",
        status="ERROR",
        details=f"Offer: {offer}. Felmérés: {adatlap_details}",
    )
    log(
        "Megrendelések létrehozása sikeresen befejeződött",
        script_name="pen_create_order",
        status="SUCCESS",
    )


try:
    adatlapok = MiniCrmAdatlapok.objects.filter(CategoryId=21, StatusId=2896).values()
    for adatlap in adatlapok:
        main(adatlap)
except Exception as e:
    log(
        "Megrendelések létrehozása sikertelen",
        script_name="pen_create_order",
        status="ERROR",
        details=f"Error: {e}. {traceback.format_exc()}",
    )
