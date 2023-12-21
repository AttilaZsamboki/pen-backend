from ..utils.logs import log
from ..utils.minicrm import get_all_adatlap_details
from ..utils.calculate_distance import calculate_distance_fn


def criteria(adatlap):
    if adatlap["Tavolsag"] and adatlap["FelmeresiDij"]:
        return False
    return True


def main():
    log(
        "Penészmentesítés távolságszámítás megkezdődött",
        "INFO",
        "pen_calculate_distance_cron",
    )
    adatlapok = get_all_adatlap_details(
        category_id=23, criteria=criteria, status_id=2927
    )
    for adatlap in adatlapok:
        stat = calculate_distance_fn(adatlap, source="cron")
        if stat == "Error":
            log(
                "Penészmentesítés távolságszámítás sikertelen",
                "ERROR",
                "pen_calculate_distance_cron",
                details=adatlap["Id"],
            )
            continue
        log(
            "Penészmentesítés távolságszámítás sikeresen lefutott",
            "SUCCESS",
            "pen_calculate_distance_cron",
            details=adatlap["Id"],
        )
    log(
        "Penészmentesítés távolságszámítás befejeződött",
        "INFO",
        "pen_calculate_distance_cron",
    )


main()
