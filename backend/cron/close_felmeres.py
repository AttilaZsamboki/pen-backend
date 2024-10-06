from ..utils.logs import log as l  # noqa
from functools import partial

from ..models import MiniCrmAdatlapok, Systems, SystemSettings
from ..utils.minicrm import MiniCrmClient
from dataclasses import dataclass


@dataclass
class Input:
    status_id: int
    system: Systems


def main(input: Input):
    SCRIPT_NAME = "pen_close_felmeres"

    log = partial(l, script_name=SCRIPT_NAME, system_id=system.system_id)

    log(
        "Átutalásos felmérés - Automatikus lezárás elindult",
        "INFO",
    )
    minicrm_client = MiniCrmClient(script_name=SCRIPT_NAME, system_id=system.system_id)

    adatlapok = MiniCrmAdatlapok.objects.filter(
        StatusId=input.status_id,
        FizetesiMod2="Átutalás",
        SzamlaSorszama2__isnull=False,
        SystemId=system.system_id,
    ).values()

    if adatlapok == []:
        log("Nincs lezárható adatlap", "INFO")
        return
    for adatlap in adatlapok:
        resp = minicrm_client.update_adatlap_fields(
            id=adatlap["Id"],
            fields={"StatusId": "Sikeres felmérés"},
        )
        if resp.status_code == 200:
            log(
                f"Az alábbi adatlapot sikeresen lezártuk: {adatlap['Id']}",
                "INFO",
            )
            continue
        log(
            "Hiba történt a lezárás során",
            "ERROR",
            details=resp.text,
        )


if __name__ == "__main__":
    for system in Systems.objects.all():
        status_id = SystemSettings.objects.get(
            system=system,
            label="Elszámolásra vár",
            type="StatusId",
            category_id="Felmérés",
        ).value
        main(Input(status_id=status_id, system=system))
