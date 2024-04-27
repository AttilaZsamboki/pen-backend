from ..utils.logs import log
from ..models import MiniCrmAdatlapok
from ..utils.calculate_distance import calculate_distance_fn


def criteria(adatlap: MiniCrmAdatlapok):
    if adatlap.Tavolsag and adatlap.FelmeresiDij:
        return False
    return True


def main():
    log(
        "Penészmentesítés távolságszámítás megkezdődött",
        "INFO",
        "pen_calculate_distance_cron",
    )
    adatlapok = [
        i
        for i in MiniCrmAdatlapok.objects.filter(CategoryId=23, StatusId=2927)
        if criteria(i)
    ]
    for adatlap in adatlapok:
        stat = calculate_distance_fn(adatlap, source="cron")
        if stat == "Error":
            log(
                "Penészmentesítés távolságszámítás sikertelen",
                "ERROR",
                "pen_calculate_distance_cron",
                details=adatlap.Id,
            )
            continue
        log(
            "Penészmentesítés távolságszámítás sikeresen lefutott",
            "SUCCESS",
            "pen_calculate_distance_cron",
            details=adatlap.Id,
        )
    log(
        "Penészmentesítés távolságszámítás befejeződött",
        "INFO",
        "pen_calculate_distance_cron",
    )


main()
