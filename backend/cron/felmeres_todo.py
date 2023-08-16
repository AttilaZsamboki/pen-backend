from ..utils.minicrm import create_to_do, get_all_adatlap_details, list_to_dos, update_adatlap_fields
from urllib.parse import urlencode
import pyshorteners


def felmeres_todo():
    def criteria(adatlap):
        if adatlap["Felmero2"]:
            return True
        return False

    adatlapok = get_all_adatlap_details(category_id=23, status_id=3023, criteria=criteria, deleted=False)
    if adatlapok == "Error":
        print("Error getting adatlapok")
        return
    for adatlap in adatlapok:
        urlap_url_base = "https://docs.google.com/forms/d/e/1FAIpQLSec2vWksE0BDpv3jtdjTaZoul4NPIZO45NYlswo5oK-ejRxnw/viewform?"
        query_params = {
            "entry.627362938": adatlap["ProjectHash"],
            "entry.1813112726": adatlap["Felmero2"],
            "entry.72642717": f"{adatlap['Telepules']} {adatlap['Iranyitoszam']} {adatlap['Cim2']}",
            "entry.24575099": adatlap["Name"]
        }
        encoded_params = urlencode(query_params)
        urlap_url = urlap_url_base + encoded_params
        s = pyshorteners.Shortener()
        short_url = s.tinyurl.short(urlap_url)
        urlap = update_adatlap_fields(id=adatlap["Id"], fields={"Urlap": short_url})
        if urlap["code"] == "Error":
            print("Error updating adatlap")
            continue
        to_dos = list_to_dos(adatlap_id=adatlap["Id"])
        if to_dos != "Error":
            if len([i for i in to_dos["Results"] if i["Type"] == 225]) > 0:
                print("Felmeres todo already exists")
                continue
            todo_comment = f"Új felmérést kaptál\nNév: {adatlap['Name']}\nCím: {adatlap['Telepules']}, {adatlap['Cim2']} {adatlap['Iranyitoszam']}, {adatlap['Orszag']}\nFizetési mód: {adatlap['FizetesiMod2']}\nÖsszeg: {adatlap['FelmeresiDij']} Ft\nA felmérő kérdőív megnyitásához kattints a következő linkre: {short_url}"
            todo = create_to_do(adatlap_id=adatlap["Id"], user=adatlap["Felmero2"], type=225, comment=todo_comment, deadline=adatlap["FelmeresIdopontja2"])
            if todo.status_code == 200:
                print(todo.json())
                continue
            print("Error creating todo")
felmeres_todo()