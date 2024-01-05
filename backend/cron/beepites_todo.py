from ..utils.minicrm import (
    list_to_dos,
    create_to_do,
    get_order_address,
    contact_details,
)
from ..utils.logs import log
from ..utils.utils import round_to_five
from ..models import Orders, MiniCrmAdatlapok, Felmeresek
import traceback


## Nem használjuk már, de a kód még jó, ezért nem töröljük ki
def main():
    script_name = "pen_beepites_todo"
    log("Beépítés feladatok készítése elindult", "INFO", script_name=script_name)
    adatlapok = MiniCrmAdatlapok.objects.filter(
        Enum1951="4374",
        Beepitok__isnull=False,
        DateTime1953__isnull=False,
    ).values()
    for adatlap in adatlapok:
        existing_todos = list_to_dos(
            adatlap["Id"],
            criteria=lambda todo: todo["Type"] == 199,
            script_name=script_name,
        )

        if existing_todos != [] and existing_todos is not None:
            log(
                "A feladat már létezik",
                "INFO",
                script_name=script_name,
                details=adatlap["Id"],
            )
            continue
        beepitok = adatlap["Beepitok"].split(", ")

        try:
            order = Felmeresek.objects.get(id=adatlap["FelmeresLink"].split("/")[-1])
        except Felmeresek.DoesNotExist:
            log(
                "Nincs megrendelés az adatlapon",
                "ERROR",
                script_name=script_name,
                details=adatlap["Id"],
            )
            continue
        except:
            log(
                "Hiba akadt a megrendelés lekérdezése közben",
                "ERROR",
                script_name=script_name,
                details=traceback.format_exc(),
            )
            continue

        order_id = Orders.objects.filter(adatlap_id=adatlap["Id"]).first().order_id
        address = get_order_address(order_id=order_id, script_name=script_name)

        if address["status"] == "Error":
            log(
                "Hiba akadt a rendelés lekérdezése közben",
                "ERROR",
                script_name=script_name,
                details=f"Response: {address['response']}. OrderId: {str(order_id)}",
            )
            return
        address = address["response"]

        contact = contact_details(adatlap_id=adatlap["Id"], script_name=script_name)
        if contact == "Error" or contact["status"] == "Error":
            log(
                "Hiba akadt a kapcsolattartó lekérdezése közben",
                "WARNING",
                script_name=script_name,
            )
            return
        contact = contact["response"]

        for beepito in beepitok:
            comment = f"""Új beépítési munkát kaptál

Ügyfél: {adatlap["Name"]}
Cím: {address["PostalCode"]}  {address["City"]}. {address["Address"]}
Tel: {contact["Phone"]} 
Email: {contact["Email"]} 

Beépítők: {adatlap["Beepitok"]} 
Beépítés ideje: {adatlap["DateTime1953"]} 
Fizetési mód: {adatlap["FizetesiMod3"]}

Teljes bruttó összeg: {str(round_to_five(order.grossOrderTotal))}Ft{f'''
Ha kedvezményt adunk a kedvezményes összeg, amit az ügyféltől el kell kérni: {round_to_five(order.grossOrderTotal - order.grossOrderTotal * 0.1)}Ft''' if adatlap["FizetesiMod3"] != "Átutalás" else ""}

Ki mérte fel: {adatlap["KiMerteFel2"]} 
Felmérés: {adatlap["FelmeresLink"]} 
Utcakép: {adatlap["Utcakep"]}

Garancia típusa: {adatlap["GaranciaTipusa"]}
{f'''Indoklás: {adatlap["Indoklás"]}
''' if adatlap["GaranciaTipusa"] == "Teljes Garancia" else ""}
Kiépítés feltétele: {adatlap["KiepitesFeltetele"]}{f'''
Feltétel: {adatlap["KiepitesFeltetelLeirasa"]}
Igazolva: {adatlap["KiepitesFelteteleIgazolva"]}
''' if adatlap["KiepitesFeltetele"] != "Nincs" else ""}
"""
            resp = create_to_do(
                adatlap["Id"],
                user=beepito,
                type=199,
                comment=comment,
                deadline=adatlap["DateTime1953"],
                script_name=script_name,
            )
            if resp.ok:
                log(
                    "Beépítés feladat létrehozva",
                    "SUCCESS",
                    script_name=script_name,
                    details=f"Adatlap: {adatlap['Id']}, Beépítő: {beepito}",
                )
                continue
            else:
                log(
                    "Hiba akadt a feladat létrehozása közben",
                    "ERROR",
                    script_name=script_name,
                    details=f"Adatlap: {adatlap['Id']}, Beépítő: {beepito}, Response: {resp.text}",
                )
                continue


main()
