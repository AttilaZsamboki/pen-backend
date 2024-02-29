from ..utils.logs import log
from ..utils.minicrm import create_order
from ..utils.minicrm_str_to_text import garancia_type_map

from ..models import Offers, Felmeresek, MiniCrmAdatlapok, Logs

import os
import dotenv
import requests
import traceback
import datetime

dotenv.load_dotenv()


def fn(adatlap: MiniCrmAdatlapok):
    log(
        "Megrendelések létrehozása elkezdődött",
        script_name="pen_create_order",
        status="START",
        data={"adatlap": adatlap.Id},
    )

    try:
        log(
            f"{adatlap.Name} megrendelés létrehozása",
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
    id = adatlap.Felmeresid
    felmeres = Felmeresek.objects.filter(id=id)
    if felmeres.exists():
        felmeres = felmeres.first()
    else:
        log(
            f"{adatlap.Name} megrendelés létrehozása sikertelen, nem létezik felmérés",
            script_name="pen_create_order",
            status="ERROR",
            details=f"Felmérés: {felmeres}",
        )
        return
    offer = Offers.objects.filter(adatlap=adatlap.Id).first()
    if offer:
        order = create_order(
            adatlap=felmeres.adatlap_id,
            offer_id=offer.id,
            adatlap_status="Szervezésre vár",
            project_data={
                "Megye2": felmeres.adatlap_id.Megye,
                "Utcakep": felmeres.adatlap_id.StreetViewUrl,
                "IngatlanKepe2": felmeres.adatlap_id.IngatlanKepe,
                "FelmeresLink": "https://app.peneszmentesites.hu/" + str(id),
                "KiMerteFel2": felmeres.adatlap_id.Felmero2,
                "FelmeresDatuma2": felmeres.adatlap_id.FelmeresIdopontja2,
                "GaranciaTipusa": (
                    garancia_type_map[felmeres.garancia] if felmeres.garancia else None
                ),
                "Indoklas": felmeres.garancia_reason,
                "KiepitesFeltetele": "Van" if felmeres.is_conditional else "Nincs",
                "KiepitesFeltetelLeirasa": felmeres.condition,
            },
        )
        if order["status"] == "error":
            if order["response"].lower() == "xml is not valid!":
                log(
                    f"{adatlap.Name} megrendelés létrehozása sikertelen, XML nem valid",
                    script_name="pen_create_order",
                    status="ERROR",
                    details=order["xml"],
                )
                return
            elif order["response"].lower() == "input doesn't look like it's an xml":
                log(
                    f"{adatlap.Name} megrendelés létrehozása sikertelen, input nem XML",
                    script_name="pen_create_order",
                    status="ERROR",
                    details=order["xml"],
                )
                return
            log(
                f"{adatlap.Name} megrendelés létrehozása sikertelen",
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
            f"{adatlap.Name} megrendelés létrehozása sikeres",
            script_name="pen_create_order",
            status="SUCCESS",
        )
        return
    log(
        f"{adatlap.Name} megrendelés létrehozása sikertelen, nem létezik felmérés",
        script_name="pen_create_order",
        status="ERROR",
        details=f"Offer: {offer}. Felmérés: {felmeres}",
    )
    log(
        "Megrendelések létrehozása sikeresen befejeződött",
        script_name="pen_create_order",
        status="SUCCESS",
    )


def main():
    try:
        adatlapok = MiniCrmAdatlapok.objects.filter(
            CategoryId=21, StatusId=2896, Deleted=0
        )
        for adatlap in adatlapok:
            if Logs.objects.filter(
                status="START",
                data__adatlap=adatlap.Id,
                time__gte=datetime.datetime.now() - datetime.timedelta(minutes=5),
            ).exists():
                continue
            fn(adatlap)
    except Exception as e:
        log(
            "Megrendelések létrehozása sikertelen",
            script_name="pen_create_order",
            status="ERROR",
            details=f"Error: {e}. {traceback.format_exc()}",
        )


main()
main()
