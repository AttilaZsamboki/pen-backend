from ..utils.logs import log
from ..utils.utils import get_spreadsheet
from ..utils.minicrm import update_todo, list_to_dos
from ..utils.minicrm_str_to_text import todo_map
from ..models import MiniCrmAdatlapok, MiniCrmTodos


class Project:
    def __init__(self, category_id: int, action_map):
        self.category_id = category_id
        self.action_map = action_map

    def get_category_id_str(self):
        return str(self.category_id)

    def close_todo(self, adatlap_id, type):
        todos = list_to_dos(
            adatlap_id,
            criteria=lambda x: x["Status"] == "Open"
            and todo_map[self.get_category_id_str()].get(x["Type"]) == type,
        )
        if todos:
            for todo in todos:
                update_todo(todo["Id"], {"Status": "Closed"})


felmeres_action_map = {
    ("Felmérés", lambda adatlap: adatlap.StatusIdStr != "Felmérésre vár"),
    (
        "Pénzügy díjbekérő",
        lambda adatlap: adatlap.StatusIdStr != "Utalásra vár",
    ),
    (
        "Pénzügyi elszámolás",
        lambda adatlap: adatlap.StatusIdStr != "Elszámolásra vár",
    ),
    (
        "Felmérés szervezés",
        lambda adatlap: adatlap.StatusIdStr
        not in ["Új érdeklődő", "Felmérés szervezés"],
    ),
    (
        "Pénzügy számlázás",
        lambda adatlap: adatlap.SzamlaSorszama2 is not None,
    ),
    (
        "Rendszerhiba E1",
        lambda adatlap: adatlap.StatusIdStr != "Felmérés előkészítés",
    ),
    (
        "Rendszerhiba E2",
        lambda adatlap: adatlap.SzamlaSorszama2 is not None,
    ),
    ("Rendszerhiba E3", lambda adatlap: adatlap.FelmeresiDij is not None),
    (
        "Új jelentkező - BOSS!",
        lambda adatlap: adatlap.StatusIdStr
        not in ["Új érdeklődő", "Felmérés szervezés"],
    ),
    (
        "Felmérés - BOSS!",
        lambda adatlap: adatlap.StatusIdStr != "Felmérésre vár",
    ),
    (
        "Pénzügy visszatérítés",
        lambda adatlap: adatlap.VisszafizetesDatuma is not None
        and adatlap.VisszafizetesDatuma != "",
    ),
    (
        "Rendszerhiba E5",
        lambda adatlap: adatlap.StatusId not in [3079, 3082],
    ),
    (
        "Rendszerhiba E4",
        lambda adatlap: MiniCrmTodos.objects.filter(todo_id=adatlap.Id).exists(),
    ),
    (
        "Rendszerhiba E6",
        lambda adatlap: MiniCrmAdatlapok.objects.filter(
            KapcsolodoFelmeres=adatlap.FelmeresAdatok
        ).exists(),
    ),
}


garancia_action_map = {
    (
        (
            "Új garancia",
            "Ügyfélkapu kapcsolat",
            "Új karbantartás",
            "Új szerviz",
            "Új bővítés",
            "Rendszerhiba E1",
            "Új jelentkező - BOSS!",
        ),
        lambda adatlap: adatlap.StatusId != 3121,
    ),
    ("Ügyfélkapu szervezés", lambda adatlap: adatlap.StatusId != 3125),
    ("Ügyfélkapu díjbekérő", lambda adatlap: adatlap.StatusId != 3127),
    (
        (
            "Ügyfélkapu kiszállás",
            "Felmérés - BOSS!",
            "Rendszergarancia",
            "Rendszerbővítés",
            "Karbantartás",
            "Szerviz",
        ),
        lambda adatlap: adatlap.StatusId != 3129,
    ),
    ("Műszaki egyeztetés", lambda adatlap: adatlap.StatusId != 3130),
    ("Ügyfélkapu számlázás", lambda adatlap: adatlap.SzamlaSorszama is not None),
    (
        "Ügyfélkapu visszafizetés",
        lambda adatlap: adatlap.VisszafizetesDatuma2 is not None,
    ),
    ("Rendszerhiba E2", lambda adatlap: adatlap.SzamlaSorszama is not None),
    ("Rendszerhiba E3", lambda adatlap: adatlap.NettoFelmeresiDij is not None),
    (
        "Rendszerhiba E4",
        lambda adatlap: MiniCrmTodos.objects.filter(todo_id=adatlap.Id).exists(),
    ),
    (
        "Rendszerhiba E5",
        lambda adatlap: adatlap.StatusId not in [3127, 3126],
    ),
}


modules = [
    Project(23, felmeres_action_map),
    Project(33, garancia_action_map),
]


def main(module: Project):
    sheet = get_spreadsheet("[SYS] ÖSSZES TEENDŐ", module.get_category_id_str())
    for row in sheet.get("B2:C"):
        if len(row) == 2:
            data = {"Id": row[0].split("/")[-1], "Type": row[1]}
            adatlap = MiniCrmAdatlapok.objects.filter(Id=data["Id"]).first()
            if adatlap is None:
                continue

            for condition in module.action_map:
                if isinstance(condition[0], tuple):
                    if data["Type"] in condition[0] and condition[1](adatlap):
                        module.close_todo(adatlap.Id, data["Type"])
                        break
                elif data["Type"] == condition[0] and condition[1](adatlap):
                    module.close_todo(adatlap.Id, data["Type"])
                    break


for module in modules:
    main(module)
