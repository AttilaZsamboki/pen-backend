from ..utils.minicrm import (
    create_to_do,
    update_adatlap_fields,
    contact_details,
)
from ..utils.utils import get_spreadsheet
from ..utils.logs import log
from ..models import MiniCrmAdatlapok


def felmeres_todo():
    script_name = "pen_felmeres_todo"
    log("Felmérés feladatok készítése elindult", "INFO", script_name=script_name)

    adatlapok = MiniCrmAdatlapok.objects.filter(
        CategoryId=23,
        StatusId=3023,
        Felmero2__isnull=False,
        FelmeresIdopontja2__isnull=False,
    ).values()
    to_dos = []
    sheet = get_spreadsheet("[SYS] ÖSSZES TEENDŐ", "Munkalap1")
    for row in sheet.get("B2:C"):
        if len(row) == 2:
            data = {"Id": row[0].split("/")[-1], "Type": row[1]}
            if data["Type"] == "Felmérés":
                to_dos.append(data)
    for adatlap in adatlapok:
        url = "https://app.peneszmentesites.hu/new?page=1&adatlap_id=" + str(
            adatlap["Id"]
        )
        urlap = update_adatlap_fields(
            id=adatlap["Id"], fields={"Urlap": url}, script_name=script_name
        )
        if urlap["code"] == "Error":
            log(
                "Hiba akadt az adatlap Urlap mezőjének frissítése közben",
                "ERROR",
                script_name=script_name,
                details="Adatlap: "
                + str(adatlap["Id"])
                + ", Error: "
                + str(urlap["reason"]),
            )
            continue
        if [i for i in to_dos if i["Id"] == str(adatlap["Id"])] == []:
            contact = contact_details(
                contact_id=adatlap["ContactId"], script_name=script_name
            )
            if contact["status"] == "Error":
                log(
                    "Hiba akadt a kapcsolat lekérdezése közben",
                    "ERROR",
                    script_name=script_name,
                    details="Adatlap: "
                    + str(adatlap["Id"])
                    + ", Error: "
                    + str(contact["response"]),
                )
                continue
            contact = contact["response"]
            todo_comment = f"Új felmérést kaptál\nNév: {adatlap['Name']}\nCím: {adatlap['Telepules']}, {adatlap['Cim2']} {adatlap['Iranyitoszam']}, {adatlap['Orszag']}\nFizetési mód: {adatlap['FizetesiMod2']}\nÖsszeg: {adatlap['FelmeresiDij']} Ft\nA felmérő kérdőív megnyitásához kattints a következő linkre: {url}\nUtcakép: {adatlap['StreetViewUrl']}\nTel: {contact['Phone']}"
            todo = create_to_do(
                adatlap_id=adatlap["Id"],
                user=adatlap["Felmero2"],
                type=225,
                comment=todo_comment,
                deadline=adatlap["FelmeresIdopontja2"],
                script_name=script_name,
            )
            if todo.status_code == 200:
                continue
            log(
                "Hiba akadt a feladat létrehozása közben",
                "ERROR",
                script_name=script_name,
                details="Adatlap: " + str(adatlap["Id"]) + ", Error: " + str(todo.text),
            )
        else:
            log(
                "A felméréshez már létezik feladat",
                "INFO",
                script_name=script_name,
                details=adatlap["Id"],
            )
            continue


felmeres_todo()
