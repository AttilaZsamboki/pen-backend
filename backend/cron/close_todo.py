import os

from ..utils.logs import log  # noqa
from ..models import MiniCrmAdatlapok, MiniCrmTodos, Systems, SystemSettings
from ..utils.minicrm import MiniCrmClient
from ..utils.minicrm_str_to_text import todo_map
from ..utils.utils import GSS


class Project:
    def __init__(self, category_id: int, action_map):
        self.category_id = category_id
        self.action_map = action_map

    def get_category_id_str(self):
        return str(self.category_id)

    def close_todo(self, adatlap_id, type):
        minicrm_client = MiniCrmClient(
            os.environ.get("PEN_MINICRM_SYSTEM_ID"),
            os.environ.get("PEN_MINICRM_API_KEY"),
            script_name="pen_close_todo",
        )

        todos = minicrm_client.list_todos(
            adatlap_id,
            criteria=lambda x: x["Status"] == "Open"
            and todo_map[self.get_category_id_str()].get(x["Type"]) == type,
        )
        if todos:
            for todo in todos:
                minicrm_client.update_todo(todo.Id, {"Status": "Closed"})


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
        lambda adatlap: adatlap.StatusIdStr
        not in ["Díjbekérő küldés", "Felmérés előkészítés"],
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
        lambda adatlap: adatlap.StatusIdStr != "ÚJ BEJELENTÉS",
    ),
    ("Ügyfélkapu szervezés", lambda adatlap: adatlap.StatusIdStr != "SZERVEZÉS"),
    ("Ügyfélkapu díjbekérő", lambda adatlap: adatlap.StatusIdStr != "DÍJBEKÉRŐ KÜLDÉS"),
    (
        (
            "Ügyfélkapu kiszállás",
            "Felmérés - BOSS!",
            "Rendszergarancia",
            "Rendszerbővítés",
            "Karbantartás",
            "Szerviz",
        ),
        lambda adatlap: adatlap.StatusIdStr != "KISZÁLLÁSRA VÁR",
    ),
    ("Műszaki egyeztetés", lambda adatlap: adatlap.StatusIdStr != "MŰSZAKI EGYEZTETÉS"),
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
}


def main(module: Project):
    client = GSS()
    sheet = client.get_spreadsheet("[SYS] ÖSSZES TEENDŐ", module.get_category_id_str())
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


if __name__ == "__main__":
    modules = []
    for system in Systems.objects.all():
        felmeres_category_id = SystemSettings.objects.get(
            system=system, label="Felmérés", type="CategoryId"
        ).value
        garancia_category_id = SystemSettings.objects.get(
            system=system, label="Garancia", type="CategoryId"
        ).value
        modules.append(Project(felmeres_category_id, felmeres_action_map))
        modules.append(Project(garancia_category_id, garancia_action_map))

    for module in modules:
        main(module)
