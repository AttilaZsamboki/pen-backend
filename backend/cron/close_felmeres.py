from ..utils.logs import log
from ..models import MiniCrmAdatlapok
from ..utils.minicrm import update_adatlap_fields


def main():
    log(
        "Átutalásos felmérés - Automatikus lezárás elindult",
        "INFO",
        script_name="pen_close_felmeres",
    )

    adatlapok = MiniCrmAdatlapok.objects.filter(
        StatusId="3084", FizetesiMod2="Átutalás", SzamlaSorszama2__isnull=False
    ).values()

    if adatlapok == []:
        log("Nincs lezárható adatlap", "INFO", script_name="pen_close_felmeres")
        return
    for adatlap in adatlapok:
        resp = update_adatlap_fields(
            id=adatlap["Id"],
            fields={"StatusId": "Sikeres felmérés"},
            script_name="pen_close_felmeres",
        )
        if resp["code"] == 200:
            log(
                f"Az alábbi adatlapot sikeresen lezártuk: {adatlap['Id']}",
                "INFO",
                script_name="pen_close_felmeres",
            )
            continue
        log(
            "Hiba történt a lezárás során",
            "ERROR",
            script_name="pen_close_felmeres",
            details=resp["reason"],
        )


main()
