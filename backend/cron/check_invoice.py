from ..utils.logs import log as l
import os
from functools import partial

import requests
from dotenv import load_dotenv
from dataclasses import dataclass

from ..models import MiniCrmAdatlapok, Systems, SystemSettings
from ..utils.minicrm import MiniCrmClient
from django.db.models import Q

load_dotenv()

TESZT_SZAMLA_AGENT_KULCS = os.environ.get("TESZT_SZAMLA_AGENT_KULCS")


@dataclass
class Input:
    name: str
    system: Systems
    test: bool = False
    status_id: int = None
    szamla_api_key: str = None


def main(input: Input):
    script_name = "pen_check_invoice" + "_" + input.name
    minicrm_client = MiniCrmClient(
        script_name=script_name,
        api_key=input.system.api_key,
        system_id=input.system.system_id,
    )
    log = partial(l, script_name=script_name, system_id=input.system.system_id)

    log("Szamlazz.hu számla ellenőrzés", "START")
    adatlapok = MiniCrmAdatlapok.objects.filter(
        ~Q(SzamlaSorszama2=""),
        Deleted="0",
        StatusId=input.status_id,
        SzamlaSorszama2__isnull=True,
        SystemId=input.system.system_id,
    )
    for adatlap in adatlapok:
        log(
            "Szamlazz.hu számla ellenőrzés",
            "INFO",
            details=f"adatlap: {adatlap.Id}",
        )
        query_xml = f"""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <xmlszamlaxml xmlns="http://www.szamlazz.hu/xmlszamlaxml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.szamlazz.hu/xmlszamlaxml https://www.szamlazz.hu/szamla/docs/xsds/agentxml/xmlszamlaxml.xsd">
                    <szamlaagentkulcs>{input.system.szamla_agent_kulcs if not input.test else TESZT_SZAMLA_AGENT_KULCS}</szamlaagentkulcs>
                        <rendelesSzam>{adatlap.Id}</rendelesSzam>
                    </xmlszamlaxml>
                """.strip()
        query_response = requests.post(
            "https://www.szamlazz.hu/szamla/",
            files={"action-szamla_agent_xml": ("invoice.xml", query_xml)},
        )
        if "szlahu_szamlaszam" in query_response.headers.keys():
            szamlaszam = query_response.headers["szlahu_szamlaszam"]
            if szamlaszam[0] == "E":
                update_resp = minicrm_client.update_adatlap_fields(
                    adatlap.Id,
                    {
                        "SzamlaSorszama2": szamlaszam,
                    },
                )
                if update_resp.status_code == 200:
                    log(
                        "Számlaszám feltöltve",
                        "INFO",
                        details=f"adatlap: {adatlap.Id}, szamlaszam: {szamlaszam}",
                    )
                    continue
                log(
                    f"Hiba akadt a számlaszám feltöltésében",
                    "ERROR",
                    details=f"adatlap: {adatlap.Id}, error: {update_resp.text}",
                    data={
                        "SzamlaSorszama2": szamlaszam,
                    },
                )
                continue
            log(
                "Nincs számla",
                "INFO",
                details=f"adatlap: {adatlap.Id}",
            )
            continue
        else:
            log(
                "Nincs díjbekérő",
                "INFO",
                details=f"adatlap: {adatlap.Id}",
            )


def update_data_felmeres(_: MiniCrmAdatlapok, szamlaszam):
    return {
        "SzamlaSorszama2": szamlaszam,
    }


if __name__ == "__main__":
    for system in Systems.objects.all():
        status_id = SystemSettings.objects.get(
            system=system, label="Felmérésre vár", type="StatusId"
        ).value
        main(
            Input(
                test=False,
                name="felmeres",
                system=system,
                status_id=status_id,
            )
        )
