from ..utils.google_maps import calculate_distance, get_street_view, get_street_view_url
from ..utils.logs import log
from ..utils.minicrm import update_adatlap_fields, get_all_adatlap_details

from ..models import Counties

import math

def process_data(data, source="webhook"):
    telephely = "Budapest, Nagytétényi út 218-220, 1225"
    address = f"{data['Cim2']} {data['Telepules']}, {data['Iranyitoszam']} {data['Orszag']}"
    gmaps_result = calculate_distance(start=telephely, end=address)
    script_name = "pen_calculate_distance_"+source
    if gmaps_result == "Error":
        log("Penészmentesítés MiniCRM webhook sikertelen", "ERROR", script_name,
            f"Hiba a Google Maps API-al való kommunikáció során {address}, adatlap id: {data['Id']}")
        return "Error"
    duration = gmaps_result["duration"] / 60
    distance = gmaps_result["distance"] // 1000
    formatted_duration = f"{math.floor(duration//60)} óra {math.floor(duration%60)} perc"
    fee_map = {
        0: 20000,
        31: 25000,
        101: 30000,
        201: 35000,
    }
    fee = fee_map[[i for i in fee_map.keys() if i < distance][-1]]
    try:
        get_street_view(location=address[0])
    except Exception as e:
        log("Penészmentesítés MiniCRM webhook hiba", "FAILED", e)
    street_view_url = get_street_view_url(location=address)
    try:
        county = Counties.objects.get(telepules=data["Telepules"]).megye
    except:
        county = ""
        log(log_value="Penészmentesítés MiniCRM webhook sikertelen", status="FAILED", script_name=script_name, details=f"Nem található megye a településhez: {data['Telepules']}")
    response = update_adatlap_fields(data["Id"], {
        "IngatlanKepe": "https://pen.dataupload.xyz/static/images/google_street_view/street_view.jpg", "UtazasiIdoKozponttol": formatted_duration, "Tavolsag": distance, "FelmeresiDij": fee, "StreetViewUrl": street_view_url, "BruttoFelmeresiDij": round(fee*1.27), "UtvonalAKozponttol": f"https://www.google.com/maps/dir/?api=1&origin=Nagytétényi+út+218,+Budapest,+1225&destination={address}&travelmode=driving", "Megye": county})
    if response["code"] == 200:
        log("Penészmentesítés MiniCRM webhook sikeresen lefutott",
            "SUCCESS", script_name)
    else:
        log("Penészmentesítés MiniCRM webhook sikertelen",
            "ERROR", script_name, response["reason"])
    return "Success"

def criteria(adatlap):
    if adatlap["Tavolsag"] and adatlap["FelmeresiDij"]:
        return False
    return True


log("Penészmentesítés távolságszámítás megkezdődött",
    "INFO", "pen_calculate_distance_cron")
adatlapok = get_all_adatlap_details(category_id=23, criteria=criteria, status_id=2927)
for adatlap in adatlapok:
    stat = process_data(adatlap, cron=True)
    if stat == "Error":
        log("Penészmentesítés távolságszámítás sikertelen",
            "ERROR", "pen_calculate_distance_cron", details=adatlap["Id"])
        continue
    log("Penészmentesítés távolságszámítás sikeresen lefutott",
        "SUCCESS", "pen_calculate_distance_cron", details=adatlap["Id"])