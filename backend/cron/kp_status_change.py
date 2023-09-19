from ..utils.minicrm import get_all_adatlap_details, update_adatlap_fields
from ..utils.logs import log 

def main():
    log("Elkeződött a készpénzes adatlapok ellenőrzése", "INFO", "pen_kp_status_change")
    def criteria(adatlap):
        if not adatlap["DijbekeroSzama2"] and adatlap["FizetesiMod2"] == "Készpénz":
            return True
        return False

    adatlapok = get_all_adatlap_details(category_id=23, status_id=3082, criteria=criteria)
    if adatlapok != "Error":
        for adatlap in adatlapok:
            update_adatlap_fields(adatlap["Id"], {"StatusId": "Felmérésre vár"})
        log("Készpénzes adatlapok átállítva 'Felmérésre vár' státuszra", "INFO", "pen_kp_status_change")
        return
    log("Hiba történt a készpénzes adatlapok ellenőrzése közben", "ERROR", "pen_kp_status_change")
main()