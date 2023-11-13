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
    for todo in todos:
        update_todo(todo["Id"], {"Status": "Closed"})


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

            def next():
                close_todo(data["Id"], data["Type"])
                continue

            if adatlap.StatusId is None:
                continue
            if data["Type"] == "Felmérés" and adatlap.StatusIdStr != "Felmérésre vár":
                next()
            elif (
                data["Type"] == "Pénzügy díjbekérő"
                and adatlap.StatusIdStr != "Utalásra vár"
            ):
                next()
            elif (
                data["Type"] == "Pénzügyi elszámolás"
                and adatlap.StatusIdStr != "Elszámolásra vár"
            ):
                next()
            elif (
                data["Type"] == "Felmérés szervezés"
                and adatlap.StatusIdStr != "Új érdeklődő"
                and adatlap.StatusIdStr != "Felmérés szervezés"
            ):
                next()
            elif (
                data["Type"] == "Pénzügy számlázás"
                and adatlap.SzamlaSorszama2 is not None
            ):
                next()
            elif (
                data["Type"] == "Rendszerhiba E1"
                and adatlap.StatusIdStr != "Felmérés előkészítés"
            ):
                next()
            elif (
                data["Type"] == "Rendszerhiba E2"
                and adatlap.SzamlaSorszama2 is not None
            ):
                next()
            elif data["Type"] == "Rendszerhiba E3" and adatlap.FelmeresiDij is not None:
                next()
            elif (
                data["Type"] == "Új jelentkező - BOSS!"
                and adatlap.StatusIdStr != "Új érdeklődő"
                and adatlap.StatusIdStr != "Felmérés szervezés"
            ):
                next()
            elif (
                data["Type"] == "Felmérés - BOSS!"
                and adatlap.StatusIdStr != "Felmérésre vár"
            ):
                next()


main()
