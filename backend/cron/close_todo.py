from ..utils.logs import log
from ..utils.utils import get_spreadsheet
from ..utils.minicrm import update_todo, list_to_dos
from ..utils.minicrm_str_to_text import todo_map
from ..models import MiniCrmAdatlapok


def close_todo(adatlap_id, type):
    todos = list_to_dos(
        adatlap_id,
        criteria=lambda x: x["Status"] == "Open" and todo_map[x["Type"]] == type,
    )
    print(adatlap_id, todos)
    return
    for todo in todos:
        update_todo(todo, {"Status": "Closed"})


def main():
    log("Összes teendő lekérdezése elindult", "INFO", script_name="close_todo")
    sheet = get_spreadsheet("[SYS] ÖSSZES TEENDŐ", "Munkalap1")
    for row in sheet.get("B2:C"):
        if len(row) == 2:
            data = {"Id": row[0].split("/")[-1], "Type": row[1]}
            adatlap = MiniCrmAdatlapok.objects.filter(Id=data["Id"]).first()
            if adatlap is None:
                log(
                    "Nincs ilyen adatlap",
                    "ERROR",
                    script_name="close_todo",
                    details=data["Id"],
                )
                continue
            if data["Type"] == "Felmérés" and adatlap.StatusIdStr != "Felmérésre vár":
                print(adatlap.StatusIdStr)
                close_todo(data["Id"], data["Type"])
                pass
            elif (
                data["Type"] == "Pénzügy díjbekérő"
                and adatlap.StatusIdStr != "Utalásra vár"
            ):
                close_todo(data["Id"], data["Type"])
            elif (
                data["Type"] == "Pénzügyi elszámolás"
                and adatlap.StatusIdStr != "Elszámolásra vár"
            ):
                close_todo(data["Id"], data["Type"])
            elif data["Type"] == "Felmérés szervezés" and (
                adatlap.StatusIdStr != "Új érdeklődő"
                or adatlap.StatusIdStr != "Felmérés szervezés"
            ):
                close_todo(data["Id"], data["Type"])
            elif (
                data["Type"] == "Pénzügy számlázás"
                and adatlap.SzamlaSorszama2 is not None
            ):
                close_todo(data["Id"], data["Type"])


main()
