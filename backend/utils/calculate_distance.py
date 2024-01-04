from ..utils.google_maps import calculate_distance, get_street_view, get_street_view_url
from ..utils.logs import log
from ..utils.minicrm import update_adatlap_fields

from ..models import Counties

import math


def calculate_distance_fn(
    data,
    source="webhook",
    address=None,
    telephely="Budapest, Nagytétényi út 218-220, 1225",
    city_field="Telepules",
    update_data=None,
):
    address = address(data)
    gmaps_result = calculate_distance(start=telephely, end=address, priorty="distance")
    script_name = "pen_calculate_distance_" + source
    if gmaps_result == "Error":
        log(
            "Penészmentesítés MiniCRM webhook sikertelen",
            "WARNING",
            script_name,
            f"Hiba a Google Maps API-al való kommunikáció során {address}, adatlap id: {data['Id']}",
        )
        return "Error"
    if type(gmaps_result) == str:
        return "Error"
    duration = gmaps_result["duration"] / 60
    distance = gmaps_result["distance"] // 1000
    formatted_duration = (
        f"{math.floor(duration//60)} óra {math.floor(duration%60)} perc"
    )
    fee_map = {
        0: 20000,
        31: 25000,
        101: 30000,
        201: 35000,
    }
    fee = fee_map[[i for i in fee_map.keys() if i < distance][-1]]
    try:
        resp = get_street_view(location=address)
        if not resp.ok:
            log(
                "Penészmentesítés MiniCRM webhook sikertelen",
                "ERROR",
                script_name,
                f"Hiba a Google Maps API-al való kommunikáció során {address}, adatlap id: {data['Id']}. Google API válasz: {resp.text}",
            )
        else:
            log(
                "Google streetview kép sikeresen mentve",
                "INFO",
                script_name,
                f"Adatlap id: {data['Id']}. URL: {resp.url}",
            )
    except Exception as e:
        log("Penészmentesítés MiniCRM webhook hiba", "FAILED", e)
    street_view_url = get_street_view_url(location=address)
    try:
        county = Counties.objects.get(telepules=data[city_field]).megye
    except:
        county = ""
        log(
            log_value="Penészmentesítés MiniCRM webhook sikertelen",
            status="FAILED",
            script_name=script_name,
            details=f"Nem található megye a településhez: {data[city_field]}",
        )
    response = update_adatlap_fields(
        data["Id"],
        update_data(
            formatted_duration, distance, fee, street_view_url, county, address
        ),
    )
    if response["code"] == 200:
        log(
            "Penészmentesítés MiniCRM webhook sikeresen lefutott",
            "SUCCESS",
            script_name,
        )
    else:
        if response["reason"] == "Too Many Requests":
            log(
                "Penészmentesítés MiniCRM webhook sikertelen",
                "WARNING",
                script_name,
                response["reason"],
            )
        else:
            log(
                "Penészmentesítés MiniCRM webhook sikertelen",
                "ERROR",
                script_name,
                response["reason"],
            )
    return "Success"
