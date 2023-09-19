from ..utils.minicrm import create_to_do, get_all_adatlap_details, list_to_dos, update_adatlap_fields
from ..utils.logs import log

def felmeres_todo():
    log("Felmérés feladatok készítése elindult", "INFO", script_name="pen_felmeres_todo")
    def criteria(adatlap):
        if adatlap["Felmero2"] and adatlap["FelmeresIdopontja2"]:
            return True
        return False

    adatlapok = get_all_adatlap_details(category_id=23, status_id=3023, criteria=criteria, deleted=False)
    if adatlapok == "Error":
        log("Hiba akadt az adatlapok lekérdezése közben", "ERROR", script_name="pen_felmeres_todo")
        return
    for adatlap in adatlapok:
        url = "https://app.peneszmentesites.hu/felmeresek/new?adatlap_id=" + str(adatlap["Id"])
        urlap = update_adatlap_fields(id=adatlap["Id"], fields={"Urlap": url})
        if urlap["code"] == "Error":
            log("Hiba akadt az adatlap Urlap mezőjének frissítése közben", "ERROR", script_name="pen_felmeres_todo", details="Adatlap: "+str(adatlap["Id"])+", Error: "+str(urlap["reason"]) )
            continue
        def tod_criteria(todo):
            if todo["Type"] == 225:
                return True
            return False
        to_dos = list_to_dos(adatlap_id=adatlap["Id"], criteria=tod_criteria)
        if to_dos != "Error" and to_dos == []:
            todo_comment = f"Új felmérést kaptál\nNév: {adatlap['Name']}\nCím: {adatlap['Telepules']}, {adatlap['Cim2']} {adatlap['Iranyitoszam']}, {adatlap['Orszag']}\nFizetési mód: {adatlap['FizetesiMod2']}\nÖsszeg: {adatlap['FelmeresiDij']} Ft\nA felmérő kérdőív megnyitásához kattints a következő linkre: {url}\nUtcakép: {adatlap['StreetViewUrl']}"
            todo = create_to_do(adatlap_id=adatlap["Id"], user=adatlap["Felmero2"], type=225, comment=todo_comment, deadline=adatlap["FelmeresIdopontja2"])
            if todo.status_code == 200:
                continue
            log("Hiba akadt a feladat létrehozása közben", "ERROR", script_name="pen_felmeres_todo", details="Adatlap: "+str(adatlap["Id"])+", Error: "+str(todo.text))
        else:
            log("A felméréshez már létezik feladat", "INFO", script_name="pen_felmeres_todo", details=adatlap["Id"])
            continue
felmeres_todo()