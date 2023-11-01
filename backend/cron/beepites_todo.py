from ..utils.minicrm import (
    get_all_adatlap_details,
    list_to_dos,
    create_to_do,
    get_order_address,
    contact_details,
    get_order,
)
from ..utils.logs import log
from ..models import Orders
import json


def criteria(adatlap):
    print(adatlap)
    return (
        adatlap["Beepitok"]
        and adatlap["DateTime1953"]
        and list_to_dos(adatlap["Id"], criteria=lambda todo: todo["Type"] == 199) == []
    )


def main():
    log(
        "Beépítés feladatok készítése elindult", "INFO", script_name="pen_beepites_todo"
    )
    adatlapok = get_all_adatlap_details(
        category_id=29, deleted=False, criteria=criteria
    )
    if adatlapok == "Error":
        log(
            "Hiba akadt az adatlapok lekérdezése közben",
            "ERROR",
            script_name="pen_beepites_todo",
        )
        return
    for adatlap in adatlapok:
        beepitok = adatlap["Beepitok"].split(", ")
        order_id = Orders.objects.filter(adatlap_id=adatlap["Id"]).first().order_id

        order = get_order(order_id=order_id)
        address = get_order_address(order=order)
        if order["status"] == "Error":
            log(
                "Hiba akadt a rendelés lekérdezése közben",
                "ERROR",
                script_name="pen_beepites_todo",
                details=f"Response: {order['response']}. OrderId: {str(order_id)}",
            )
            return
        order = order["response"]

        if address["status"] == "Error":
            log(
                "Hiba akadt a rendelés lekérdezése közben",
                "ERROR",
                script_name="pen_beepites_todo",
                details=f"Response: {address['response']}. OrderId: {str(order_id)}",
            )
            return
        address = address["response"]

        contact = contact_details(adatlap_id=adatlap["Id"])
        if contact == "Error":
            log(
                "Hiba akadt a kapcsolattartó lekérdezése közben",
                "ERROR",
                script_name="pen_beepites_todo",
            )
            return
        contact = contact["response"]

        print(json.dumps(order, indent=4))
        for beepito in beepitok:
            comment = f"""Új beépítési munkát kaptál
Ügyfél: {adatlap["Name"]}
Cím: {address["PostalCode"]}  {address["City"]}. {address["Address"]}
Tel: {contact["Phone"]} 
Email: {contact["Email"]} 

Beépítők: {adatlap["Beepitok"]} 
Beépítés ideje: {adatlap["DateTime1953"]} 
Fizetési mód: {adatlap["FizetesiMod3"]}
Ki mérte fel: {adatlap["KiMerteFel2"]} 

Raktár: https://app.clouderp.hu/v2/order?view=68&search={adatlap["RendelesSzama"]}
Felmérés: {adatlap["FelmeresLink"]} 
Utcakép: {adatlap["Utcakep"]}

Megrendelés bruttó: {order["Amount"].replace(".0000", "")}Ft
Megrendelés nettó: {order["AmountNet"].replace(".0000", "")}Ft"""
            resp = create_to_do(
                adatlap["Id"],
                user=beepito,
                type=199,
                comment=comment,
                deadline=adatlap["DateTime1953"],
            )
            if resp.ok:
                log(
                    "Beépítés feladat létrehozva",
                    "SUCCESS",
                    script_name="pen_beepites_todo",
                    details=f"Adatlap: {adatlap['Id']}, Beépítő: {beepito}",
                )
                continue
            else:
                log(
                    "Hiba akadt a feladat létrehozása közben",
                    "ERROR",
                    script_name="pen_beepites_todo",
                    details=f"Adatlap: {adatlap['Id']}, Beépítő: {beepito}, Response: {resp.text}",
                )
                continue


main()
