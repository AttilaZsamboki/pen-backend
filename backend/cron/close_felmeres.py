from ..utils.logs import log as l  # noqa
from functools import partial

from ..models import MiniCrmAdatlapok
from ..utils.minicrm import MiniCrmClient


def main():
    script_name = "pen_close_felmeres"
    log = partial(l, script_name=script_name)

    log(
        "Átutalásos felmérés - Automatikus lezárás elindult",
        "INFO",
    )
    minicrm_client = MiniCrmClient(script_name=script_name)

    adatlapok = MiniCrmAdatlapok.objects.filter(
        StatusId="3084", FizetesiMod2="Átutalás", SzamlaSorszama2__isnull=False
    ).values()

    if adatlapok == []:
        log("Nincs lezárható adatlap", "INFO")
        return
    for adatlap in adatlapok:
        resp = minicrm_client.update_adatlap_fields(
            id=adatlap["Id"],
            fields={"StatusId": "Sikeres felmérés"},
            script_name="pen_close_felmeres",
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


main()
