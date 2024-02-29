from ..utils.minicrm import (
    create_to_do,
    update_adatlap_fields,
    get_order_address,
    contact_details,
)
from ..utils.minicrm_str_to_text import todo_map
from ..utils.utils import round_to_five
from ..utils.logs import log
from ..models import MiniCrmAdatlapok, MiniCrmTodos, Orders, Felmeresek, Logs
import traceback
from datetime import datetime, timedelta


def main(
    status_id=None,
    filter_adatlapok=lambda _: True,
    update_adatlap=None,
    script_name=None,
    todo_comment=None,
    user_field=None,
    deadline_field=None,
    type=0,
    custom_create_todo=None,
    does_todo_exist=None,
):
    script_name = script_name + "_todo"
    log("Felmérés feladatok készítése elindult", "INFO", script_name=script_name)

    adatlapok = [
        i
        for i in (
            MiniCrmAdatlapok.objects.filter(
                StatusId=status_id,
            )
            if status_id is not None
            else MiniCrmAdatlapok.objects.all()
        )
        if filter_adatlapok(i)
    ]

    for adatlap in adatlapok:
        if (
            does_todo_exist(adatlap)
            if does_todo_exist
            else MiniCrmTodos.objects.filter(todo_id=adatlap.Id).exists() is False
        ):
            if Logs.objects.filter(
                script_name=script_name,
                details=adatlap.Id,
                status="START",
                time__gte=datetime.now() - timedelta(minutes=5),
            ).exists():
                continue
            log(
                "Új feladat létrehozása",
                "START",
                script_name=script_name,
                details=adatlap.Id,
            )
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
            todo_comment_str = todo_comment(adatlap=adatlap, contact=contact)
            if custom_create_todo is not None:
                custom_create_todo(
                    adatlap=adatlap,
                    type=type(adatlap),
                    comment=todo_comment_str,
                    deadline=adatlap.__dict__[deadline_field],
                    script_name=script_name,
                )
            else:
                todo = create_to_do(
                    adatlap_id=adatlap.Id,
                    user=adatlap.__dict__[user_field],
                    type=type(adatlap),
                    comment=todo_comment_str,
                    deadline=adatlap.__dict__[deadline_field],
                    script_name=script_name,
                )
                if todo.status_code == 200:
                    MiniCrmTodos(todo_id=adatlap.Id).save()
                    continue
                log(
                    "Hiba akadt a feladat létrehozása közben",
                    "ERROR",
                    script_name=script_name,
                    details="Adatlap: "
                    + str(adatlap.Id)
                    + ", Error: "
                    + str(todo.text),
                )


def filter_adatlapok(adatlap: MiniCrmAdatlapok):
    if adatlap.Felmero2 is None or adatlap.FelmeresIdopontja2 is None:
        return False
    return True


def update_adatlap(adatlap: MiniCrmAdatlapok):
    return {
        "Urlap": "https://app.peneszmentesites.hu/new?page=1&adatlap_id="
        + str(adatlap.Id)
    }


def felmeres_comment(adatlap: MiniCrmAdatlapok, contact: dict):
    return f"Új felmérést kaptál\nNév: {adatlap.Name}\nCím: {adatlap.Iranyitoszam} {adatlap.Telepules} {adatlap.Cim2}, {adatlap.Orszag}\nFizetési mód: {adatlap.FizetesiMod2}\nÖsszeg: {adatlap.FelmeresiDij} Ft\nA felmérő kérdőív megnyitásához kattints a következő linkre: https://app.peneszmentesites.hu/new?page=1&adatlap_id={str(adatlap.Id)}\nUtcakép: {adatlap.StreetViewUrl}\nTel: {contact['Phone']}"


def garancia_comment(adatlap: MiniCrmAdatlapok, contact: dict):
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


def beepites_comment(adatlap: MiniCrmAdatlapok, contact: dict):
    script_name = "pen_beepites_todo"
    order_id = Orders.objects.filter(adatlap_id=adatlap.Id).first().order_id
    address = get_order_address(order_id=order_id, script_name=script_name)

    try:
        order = Felmeresek.objects.get(id=adatlap.FelmeresLink.split("/")[-1])
    except Felmeresek.DoesNotExist:
        log(
            "Nincs megrendelés az adatlapon",
            "ERROR",
            script_name=script_name,
            details=adatlap.Id,
        )
        return
    except:
        log(
            "Hiba akadt a megrendelés lekérdezése közben",
            "ERROR",
            script_name=script_name,
            details=traceback.format_exc(),
        )
        return

    if address["status"] == "Error":
        log(
            "Hiba akadt a rendelés lekérdezése közben",
            "ERROR",
            script_name="pen_beepites_todo",
            details=f"Response: {address['response']}. OrderId: {str(order_id)}",
        )
        return
    address = address["response"]
    return f"""Új beépítési munkát kaptál

Ügyfél: {adatlap.Name}
Cím: {address["PostalCode"]}  {address["City"]}. {address["Address"]}
Tel: {contact["Phone"]} 
Email: {contact["Email"]} 

Beépítők: {adatlap.Beepitok} 
Beépítés ideje: {adatlap.DateTime1953.strftime("%Y-%m-%d %H:%M:%S")} 
Fizetési mód: {adatlap.FizetesiMod3}

Teljes bruttó összeg: {str(round_to_five(order.grossOrderTotal))}Ft{f'''
Ha kedvezményt adunk a kedvezményes összeg, amit az ügyféltől el kell kérni: {round_to_five(order.grossOrderTotal - order.grossOrderTotal * 0.1)}Ft''' if adatlap.FizetesiMod3 != "Átutalás" else ""}

Ki mérte fel: {adatlap.KiMerteFel2} 
Felmérés: {adatlap.FelmeresLink} 
Utcakép: {adatlap.Utcakep}

Garancia típusa: {adatlap.GaranciaTipusa}
{f'''Indoklás: {adatlap.Indoklás}
''' if adatlap.GaranciaTipusa == "Teljes Garancia" else ""}
Kiépítés feltétele: {adatlap.KiepitesFeltetele}{f'''
Feltétel: {adatlap.KiepitesFeltetelLeirasa}
Igazolva: {adatlap.KiepitesFelteteleIgazolva}
''' if adatlap.KiepitesFeltetele != "Nincs" else ""}
"""


def create_beepites_todo(
    adatlap: MiniCrmAdatlapok, type: int, comment: str, deadline: str, script_name: str
):
    beepitok = adatlap.Beepitok.split(", ")
    for beepito in beepitok:
        todo = create_to_do(
            adatlap_id=adatlap.Id,
            user=beepito,
            type=type,
            comment=comment,
            deadline=deadline,
            script_name=script_name,
        )
        if todo.status_code == 200:
            MiniCrmTodos(todo_id=str(adatlap.Id) + beepito).save()
            continue
        log(
            "Hiba akadt a feladat létrehozása közben",
            "ERROR",
            script_name=script_name,
            details="Adatlap: " + str(adatlap.Id) + ", Error: " + str(todo.text),
        )


def filter_beepites_adatlapok(adatlap: MiniCrmAdatlapok):
    return (
        adatlap.Enum1951 == "Beépítésre vár"
        and adatlap.Beepitok is not None
        and adatlap.DateTime1953 is not None
        and adatlap.StatusId != "3009"
    )


models = [
    {
        "status_id": "3023",
        "filter_adatlapok": filter_adatlapok,
        "update_adatlap": update_adatlap,
        "script_name": "pen_felmeres",
        "user_field": "Felmero2",
        "todo_comment": felmeres_comment,
        "deadline_field": "FelmeresIdopontja2",
        "type": lambda _: 225,
    },
    {
        "status_id": "3129",
        "script_name": "pen_garancia",
        "user_field": "GaranciaFelmerestVegzi",
        "filter_adatlapok": lambda adatlap: adatlap.BejelentesTipusa is not None
        and adatlap.GaranciaFelmerestVegzi is not None,
        "todo_comment": garancia_comment,
        "deadline_field": "FelmeresDatuma3",
        "type": lambda adatlap: [
            j for j, k in todo_map["33"].items() if k == adatlap.BejelentesTipusa
        ],
    },
    {
        "script_name": "pen_beepites",
        "filter_adatlapok": filter_beepites_adatlapok,
        "todo_comment": beepites_comment,
        "deadline_field": "DateTime1953",
        "type": lambda _: 199,
        "custom_create_todo": create_beepites_todo,
        "does_todo_exist": lambda adatlap: any(
            not MiniCrmTodos.objects.filter(todo_id=str(adatlap.Id) + beepito).exists()
            for beepito in adatlap.Beepitok.split(", ")
        ),
    },
]

for i in models:
    main(**i)
