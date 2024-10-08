from ..utils.google_maps import calculate_distance, get_street_view, get_street_view_url
from ..utils.logs import log
from ..utils.minicrm import MiniCrmClient
from ..services.minicrm import MiniCRMWrapper

from ..models import Counties, MiniCrmAdatlapok

import math


class CalculateDistance(MiniCRMWrapper):
    def fn(
        self,
        data: MiniCrmAdatlapok,
        source="webhook",
        address=None,
        telephely=None,
        update_data=None,
    ):
        address = address(data)
        gmaps_result = calculate_distance(
            start=telephely, end=address, priorty="distance"
        )
        self.script_name = "pen_calculate_distance_" + source
        if gmaps_result == "Error":
            self.log(
                "Penészmentesítés MiniCRM webhook sikertelen",
                "FAILED",
                f"Hiba a Google Maps API-al való kommunikáció során {address}, adatlap id: {data.Id}",
            )
            return "Error"
        if type(gmaps_result) == str:
            return "Error"
        duration = gmaps_result["duration"] / 60
        distance = math.ceil(gmaps_result["distance"] / 1000)
        formatted_duration = (
            f"{math.floor(duration//60)} óra {math.floor(duration%60)} perc"
        )
        fee_map = {
            0: 20000,
            31: 25000,
            101: 30000,
            201: 35000,
        }
        if not distance:
            self.log(
                "Távolság 0",
                "FAILED",
                f"Adatlap id: {data.Id}. Cím: {address}",
            )
            return "Error"
        fee = fee_map[[i for i in fee_map.keys() if i < distance][-1]]
        try:
            resp = get_street_view(location=address)
            if not resp.ok:
                self.log(
                    "Penészmentesítés MiniCRM webhook sikertelen",
                    "ERROR",
                    f"Hiba a Google Maps API-al való kommunikáció során {address}, adatlap id: {data.Id}. Google API válasz: {resp.text}",
                )
            else:
                self.log(
                    "Google streetview kép sikeresen mentve",
                    "INFO",
                    f"Adatlap id: {data.Id}. URL: {resp.url}",
                )
        except Exception as e:
            self.log("Penészmentesítés MiniCRM webhook hiba", "FAILED", e)
        street_view_url = get_street_view_url(location=address)
        try:
            county = Counties.objects.get(telepules=data.Telepules).megye
        except:
            county = ""
            self.log(
                log_value="Penészmentesítés MiniCRM webhook sikertelen",
                status="FAILED",
                details=f"Nem található megye a településhez: {data.Telepules}",
            )
        data_to_update = update_data(
            formatted_duration, distance, fee, street_view_url, county, address
        )

        response = self.minicrm_client.update_adatlap_fields(data.Id, data_to_update)
        if response["code"] == 200:
            self.log(
                "Penészmentesítés MiniCRM webhook sikeresen lefutott",
                "SUCCESS",
                data.Id,
            )
        else:
            if response["reason"] == "Too Many Requests":
                self.log(
                    "Penészmentesítés MiniCRM webhook sikertelen",
                    "WARNING",
                    response["reason"],
                    data_to_update,
                )
            else:
                self.log(
                    "Penészmentesítés MiniCRM webhook sikertelen",
                    "ERROR",
                    response["reason"],
                    data_to_update,
                )
        return "Success"
