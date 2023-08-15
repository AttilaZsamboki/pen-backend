from ..utils.minicrm import get_all_adatlap, update_adatlap_fields, get_adatlap_details
from ..utils.logs import log 

def main():
    log("Elkeződött a készpénzes adatlapok ellenőrzése", "INFO", "pen_kp_status_change")
    adatlapok = get_all_adatlap(category_id=23, status_id=3082)
    if adatlapok != "Error":
        adatlapok = adatlapok["Results"]
        for adatlap in adatlapok:
            adatlap = get_adatlap_details(adatlap)
            if "FizetesiMod2" not in adatlap.keys():
                continue
            if adatlap["FizetesiMod2"] == "Készpénz" and "DijbekeroSzama2" not in adatlap.keys():
                update_adatlap_fields(adatlap["Id"], {"StatusId": "Felmérésre vár"})
                return
        log("Készpénzes adatlapok átállítva 'Felmérésre vár' státuszra", "INFO", "pen_kp_status_change")
main()