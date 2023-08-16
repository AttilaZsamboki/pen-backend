from ..utils.minicrm import update_all_status
from ..utils.logs import log

def main():
    log("Átutalásos felmérés - Automatikus lezárás elindult", "INFO", script_name="pen_close_felmeres")
    def condition(adatlap):
        if adatlap["StatusId"] == "Elszámolásra vár" and adatlap["FizetesiMod2"] == "Átutalás" and adatlap["SzamlaSorszama2"] != "":
            return True
        return False
    adatlapok = update_all_status(category_id=23, status="Sikeres felmérés", condition=condition)
    if adatlapok == []:
        log("Nincs lezárható adatlap", "INFO", script_name="pen_close_felmeres")
        return
    log(f"Az alábbi adatlapokat sikeresen lezártuk: {', '.join([str(i['data']['Id']) for i in adatlapok if i['code'] == 200])}", "INFO", script_name="pen_close_felmeres")
main()