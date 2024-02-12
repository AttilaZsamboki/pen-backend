from ..utils.logs import log
import xml.etree.ElementTree as ET
import requests
import os
from dotenv import load_dotenv
from ..models import MiniCrmAdatlapok
from ..utils.minicrm import update_adatlap_fields
import datetime
import traceback

load_dotenv()


def main(
    StatusId="",
    UpdateAdatlap=None,
    test=False,
):
    log(
        "Kifizetettt számlák csekkolása megkezdődött",
        script_name="pen_paid_invoice",
        status="INFO",
    )

    SZAMLA_AGENT_KULCS = (
        os.environ.get("SZAMLA_AGENT_KULCS")
        if not test
        else os.environ.get("TESZT_SZAMLA_AGENT_KULCS")
    )

    for adatlap in MiniCrmAdatlapok.objects.filter(StatusId=StatusId):
        query_xml = f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <xmlszamlaxml xmlns="http://www.szamlazz.hu/xmlszamlaxml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.szamlazz.hu/xmlszamlaxml https://www.szamlazz.hu/szamla/docs/xsds/agentxml/xmlszamlaxml.xsd">
                <szamlaagentkulcs>{SZAMLA_AGENT_KULCS}</szamlaagentkulcs>
                    <rendelesSzam>{adatlap.Id}</rendelesSzam>
                </xmlszamlaxml>
            """.strip()
        query_response = requests.post(
            "https://www.szamlazz.hu/szamla/",
            files={"action-szamla_agent_xml": ("invoice.xml", query_xml)},
        )
        print(adatlap.Id, query_response.text)
        if query_response.status_code != 200:
            log(
                "Számla lekérdezése sikertelen",
                script_name="pen_paid_invoice",
                status="ERROR",
                details=query_response.reason,
            )
            continue

        root = ET.fromstring(query_response.text)

        # Define the namespace
        ns = {"szamla": "http://www.szamlazz.hu/szamla"}

        # Use the namespace in the search string
        brutto = root.find(".//szamla:brutto", ns)
        osszeg = root.find(".//szamla:osszeg", ns)

        if osszeg is not None and brutto is not None:
            if brutto.text == osszeg.text:
                log(
                    "Kifizetett számla",
                    script_name="pen_paid_invoice",
                    status="INFO",
                    details="Adatlap ID: " + str(adatlap.Id),
                )
                resp = update_adatlap_fields(adatlap.Id, UpdateAdatlap(adatlap))
                if resp["code"] == 200:
                    log(
                        "Adatlap frissítve",
                        script_name="pen_paid_invoice",
                        status="INFO",
                        details="Adatlap ID: " + str(adatlap.Id),
                    )
                else:
                    log(
                        "Adatlap frissítése sikertelen",
                        script_name="pen_paid_invoice",
                        status="ERROR",
                        details=resp["reason"],
                    )


def update_felmeres_adatlap(adatlap: MiniCrmAdatlapok):
    return {
        "StatusId": "3023",
        "BefizetesMegerkezett": "Igen",
        "DijbekeroUzenetek": (
            adatlap.DijbekeroUzenetek
            if adatlap.DijbekeroUzenetek
            else ""
            + f"\nBefizetés megérkezett Számlázz.hu-n keresztül: {datetime.datetime.now()}"
        ),
    }


def update_garancia_adatlap(adatlap: MiniCrmAdatlapok):
    return {
        "StatusId": "3129",
        "BefizetesMegerkezett2": "Igen",
        "DijbekeroUzenetek2": (
            adatlap.DijbekeroUzenetek if adatlap.DijbekeroUzenetek else ""
        )
        + f"\nBefizetés megérkezett Számlázz.hu-n keresztül: {datetime.datetime.now()}",
    }


modules = [
    {"StatusId": 3083, "UpdateAdatlap": update_felmeres_adatlap},
    {
        "StatusId": 3128,
        "UpdateAdatlap": update_garancia_adatlap,
        "test": True,
    },
]

try:
    for i in modules:
        main(**i)
except Exception as e:
    log(
        "Kifizetett számlák csekkolása sikertelen",
        script_name="pen_paid_invoice",
        status="ERROR",
        details=traceback.format_exc(),
    )
