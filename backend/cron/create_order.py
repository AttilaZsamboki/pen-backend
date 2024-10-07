from ..utils.logs import log as l
import os
import traceback
from functools import partial

import dotenv

from ..models import Felmeresek, MiniCrmAdatlapok, Offers, Systems
from ..utils.minicrm import MiniCrmClient
from ..utils.minicrm_str_to_text import garancia_type_map

dotenv.load_dotenv()


def fn(adatlap: MiniCrmAdatlapok, system: Systems):

    script_name = "pen_create_order"
    log = partial(l, script_name=script_name, system_id=input.system.system_id)
    log(
        "Megrendelések létrehozása elkezdődött",
        status="START",
        data={"adatlap": adatlap.Id},
    )
    minicrm_client = MiniCrmClient(
        system.system_id,
        system.api_key,
        script_name=script_name,
    )

    try:
        log(
            f"{adatlap.Name} megrendelés létrehozása",
            status="INFO",
        )
    except Exception as e:
        log(
            f"Adatlap nevének lekérése sikertelen, Error: {e}",
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
            status="ERROR",
            details=f"Felmérés: {felmeres}",
        )
        return
    offer = Offers.objects.filter(adatlap=adatlap.Id).first()
    if offer:
        order = minicrm_client.create_order(
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
        if order.ok:
            if order.lower() == "xml is not valid!":
                log(
                    f"{adatlap.Name} megrendelés létrehozása sikertelen, XML nem valid",
                    status="ERROR",
                    details=order["xml"],
                )
                return
            elif order.lower() == "input doesn't look like it's an xml":
                log(
                    f"{adatlap.Name} megrendelés létrehozása sikertelen, input nem XML",
                    status="ERROR",
                    details=order["xml"],
                )
                return
            log(
                f"{adatlap.Name} megrendelés létrehozása sikertelen",
                status="ERROR",
                details=order,
            )
            return

        resp = minicrm_client.update_adatlap_fields(
            adatlap.Id,
            fields={"StatusId": "Sikeres megrendelés"},
        )
        if resp.status_code != 200:
            log(
                f"{adatlap['Name']} megrendelés létrehozása sikertelen, megrendelés státusz frissítése sikertelen",
                script_name=script_name,
                status="ERROR",
                details=resp.text,
            )
            return
        log(
            f"{adatlap.Name} megrendelés létrehozása sikeres",
            status="SUCCESS",
        )
        return
    log(
        f"{adatlap.Name} megrendelés létrehozása sikertelen, nem létezik felmérés",
        status="ERROR",
        details=f"Offer: {offer}. Felmérés: {felmeres}",
    )
    log(
        "Megrendelések létrehozása sikeresen befejeződött",
        status="SUCCESS",
    )


def main(system: Systems):
    try:
        adatlapok = MiniCrmAdatlapok.objects.filter(
            CategoryIdStr="Ajánlat",
            StatusIdStr="Elfogadott ajánlat",
            Deleted=0,
            SystemId=system.system_id,
        )
        for adatlap in adatlapok:
            fn(adatlap)
    except Exception as e:
        l(
            "Megrendelések létrehozása sikertelen",
            script_name="pen_create_order",
            status="ERROR",
            details=f"Error: {e}. {traceback.format_exc()}",
        )


if __name__ == "__main__":
    for system in Systems.objects.all():
        main(system)
