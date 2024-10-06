from ..utils.logs import log
from ..models import MiniCrmAdatlapok, Systems, SystemSettings
from ..utils.calculate_distance import calculate_distance_fn
from dataclasses import dataclass


@dataclass
class Input:
    CategoryId: int
    StatusId: int
    System: Systems


def criteria(adatlap: MiniCrmAdatlapok):
    if adatlap.Tavolsag and adatlap.FelmeresiDij:
        return False
    return True


def main(input: Input):
    log(
        "Penészmentesítés távolságszámítás megkezdődött",
        "START",
        "pen_calculate_distance_cron",
        system_id=input.SystemId,
    )
    adatlapok = MiniCrmAdatlapok.objects.filter(
        CategoryId=input.CategoryId,
        StatusId=input.StatusId,
        SystemId=input.SystemId,
        Tavolsag__isnull=True,
        FelmeresiDij__isnull=True,
    )
    for adatlap in adatlapok:
        stat = calculate_distance_fn(
            adatlap, source="cron", telephely=input.System.telephely
        )
        if stat == "Error":
            log(
                "Penészmentesítés távolságszámítás sikertelen",
                "ERROR",
                "pen_calculate_distance_cron",
                details=adatlap.Id,
                system_id=input.SystemId,
            )
            continue
        log(
            "Penészmentesítés távolságszámítás sikeresen lefutott",
            "SUCCESS",
            "pen_calculate_distance_cron",
            details=adatlap.Id,
            system_id=input.SystemId,
        )
    log(
        "Penészmentesítés távolságszámítás befejeződött",
        "END",
        "pen_calculate_distance_cron",
        system_id=input.SystemId,
    )


if __name__ == "__main__":
    for system in Systems.objects.all():
        category_id = SystemSettings.objects.get(
            system=system, label="Felmérés", type="Category_Id"
        ).value
        status_id = SystemSettings.objects.get(
            system=system, label="Új érdeklődő", type="Status_Id"
        ).value
        if category_id and status_id:
            main(
                Input(
                    CategoryId=category_id,
                    StatusId=status_id,
                    System=system,
                )
            )
