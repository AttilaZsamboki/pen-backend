from ..utils.minicrm import update_adatlap_fields
from ..models import MiniCrmAdatlapok
from ..utils.logs import log


def main():
    log("Elkeződött a készpénzes adatlapok ellenőrzése", "INFO", "pen_kp_status_change")

    adatlapok = MiniCrmAdatlapok.objects.filter(
        CategoryId=23,
        StatusId=3082,
        DijbekeroSzama2__isnull=True,
        FizetesiMod2="Készpénz",
    ).values("Id")
    for adatlap in adatlapok:
        update_adatlap_fields(adatlap["Id"], {"StatusId": "Felmérésre vár"})
    log(
        "Készpénzes adatlapok átállítva 'Felmérésre vár' státuszra",
        "INFO",
        "pen_kp_status_change",
    )
    return


main()
