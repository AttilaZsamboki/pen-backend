from ..utils.minicrm import (
    create_to_do,
    update_adatlap_fields,
    contact_details,
)
from ..utils.minicrm_str_to_text import todo_map
from ..utils.logs import log
from ..models import MiniCrmAdatlapok, MiniCrmTodos


def main(
    status_id,
    filter_adatlapok=lambda _: True,
    update_adatlap=None,
    script_name=None,
    todo_comment=None,
    user_field=None,
    deadline_field=None,
    type=0,
):
    script_name = script_name + "_todo"
    log("Felmérés feladatok készítése elindult", "INFO", script_name=script_name)

    adatlapok = [
        i
        for i in MiniCrmAdatlapok.objects.filter(
            StatusId=status_id,
        )
        if filter_adatlapok(i)
    ]

    for adatlap in adatlapok:
        if MiniCrmTodos.objects.filter(projectid=adatlap.Id).exists() is False:
            urlap = {"url": None}
            if update_adatlap is not None:
                urlap = update_adatlap_fields(
                    id=adatlap.Id,
                    fields=update_adatlap(adatlap),
                    script_name=script_name,
                )
                if urlap["code"] == "Error":
                    log(
                        "Hiba akadt az adatlap egyik mezőjének frissítése közben",
                        "ERROR",
                        script_name=script_name,
                        details="Adatlap: "
                        + str(adatlap["Id"])
                        + ", Error: "
                        + str(urlap["reason"]),
                    )
            contact = contact_details(
                contact_id=adatlap.ContactId, script_name=script_name
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
            todo_comment = todo_comment(
                adatlap=adatlap, contact=contact, url=urlap["url"]
            )
            todo = create_to_do(
                adatlap_id=adatlap.Id,
                user=adatlap.__dict__[user_field],
                type=type(adatlap),
                comment=todo_comment,
                deadline=adatlap.__dict__[deadline_field],
                script_name=script_name,
            )
            if todo.status_code == 200:
                MiniCrmTodos(projectid=adatlap.Id).save()
                continue
            log(
                "Hiba akadt a feladat létrehozása közben",
                "ERROR",
                script_name=script_name,
                details="Adatlap: " + str(adatlap.Id) + ", Error: " + str(todo.text),
            )
        else:
            log(
                "A felméréshez már létezik feladat",
                "INFO",
                script_name=script_name,
                details=adatlap.Id,
            )
            continue


def filter_adatlapok(adatlap: MiniCrmAdatlapok):
    if adatlap.Felmero2 is None or adatlap.FelmeresIdopontja2 is None:
        return False
    return True


def update_adatlap(adatlap: MiniCrmAdatlapok):
    return {
        "Urlap": "https://app.peneszmentesites.hu/new?page=1&adatlap_id="
        + str(adatlap.Id)
    }


def felmeres_todo_comment(adatlap: MiniCrmAdatlapok, contact: dict, url: str):
    return f"Új felmérést kaptál\nNév: {adatlap['Name']}\nCím: {adatlap['Iranyitoszam']} {adatlap['Telepules']} {adatlap['Cim2']}, {adatlap['Orszag']}\nFizetési mód: {adatlap['FizetesiMod2']}\nÖsszeg: {adatlap['FelmeresiDij']} Ft\nA felmérő kérdőív megnyitásához kattints a következő linkre: {url}\nUtcakép: {adatlap['StreetViewUrl']}\nTel: {contact['Phone']}"


def garancia_todo_comment(adatlap: MiniCrmAdatlapok, contact: dict, url: str):
    return f"""Új {adatlap.BejelentesTipusa} feladatot kaptál!

Név: {contact["FirstName"]} {contact["LastName"]}
Email: {contact["Email"]}
Telefon:{contact["Phone"]}
Cím: {adatlap.Iranyitoszam2}. {adatlap.Telepules2}, {adatlap.Cim3}, {adatlap.Orszag2}
Útvonal a központtól: {adatlap.UtvonalAKozponttol}
**********************
Bejelentés típusa: {adatlap.BejelentesTipusa}
Bejelentés szövege: "{adatlap.BejelentesSzovege}"

Ha már elvégezted a feladatot akkor zárd le ezt a teendőt!"""


models = [
    {
        "status_id": "3023",
        "filter_adatlapok": filter_adatlapok,
        "update_adatlap": update_adatlap,
        "script_name": "pen_felmeres",
        "user_field": "Felmero2",
        "todo_comment": felmeres_todo_comment,
        "deadline_field": "FelmeresIdopontja2",
        "type": lambda _: 225,
    },
    {
        "status_id": "3129",
        "script_name": "pen_garancia",
        "user_field": "GaranciaFelmerestVegzi",
        "filter_adatlapok": lambda adatlap: adatlap.BejelentesTipusa is not None
        and adatlap.GaranciaFelmerestVegzi is not None,
        "todo_comment": garancia_todo_comment,
        "deadline_field": "FelmeresDatuma3",
        "type": lambda adatlap: [
            j for j, k in todo_map.items() if k == adatlap.BejelentesTipusa
        ],
    },
]

for i in models:
    main(**i)
