from ..utils.minicrm import get_all_adatlap, update_adatlap_fields, get_adatlap_details
from ..utils.logs import log 

def main():
    log("Elkeződött a készpénzes adatlapok ellenőrzése", "INFO", "pen_kp_status_change")
    adatlapok = get_all_adatlap(category_id=23, status_id=3082)
    if adatlapok != "Error":
        for adatlap in adatlapok["Results"]:
            adatlap = get_adatlap_details(adatlap)
            if "FizetesiMod2" not in adatlap.keys() or ("DijbekeroSzama2" in adatlap.keys() and adatlap["DijbekeroSzama2"] != ""):
                continue
            if adatlap["FizetesiMod2"] == "Készpénz":
                update_adatlap_fields(adatlap["Id"], {"StatusId": "Felmérésre vár"})
                continue
        log("Készpénzes adatlapok átállítva 'Felmérésre vár' státuszra", "INFO", "pen_kp_status_change")
        return
    log("Hiba történt a készpénzes adatlapok ellenőrzése közben", "ERROR", "pen_kp_status_change")
main()