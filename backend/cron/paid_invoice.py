from ..utils.logs import log
import xml.etree.ElementTree as ET
import requests
import os
from dotenv import load_dotenv
from ..models import MiniCrmAdatlapok
from ..utils.minicrm import update_adatlap_fields
import datetime

load_dotenv()

SZAMLA_AGENT_KULCS = os.environ.get("SZAMLA_AGENT_KULCS")


def main():
    log(
        "Kifizetettt számlák csekkolása megkezdődött",
        script_name="pen_paid_invoice",
        status="INFO",
    )
    for adatlap in MiniCrmAdatlapok.objects.filter(CategoryId="23", StatusId="3083"):
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
        brutto = root.find(".//szamla:brutto", ns).text
        osszeg = root.find(".//szamla:osszeg", ns)

        if osszeg is not None:
            if brutto == osszeg.text:
                log(
                    "Kifizetett számla",
                    script_name="pen_paid_invoice",
                    status="INFO",
                    details="Adatlap ID: " + str(adatlap.Id),
                )
                resp = update_adatlap_fields(
                    adatlap.Id,
                    {
                        "StatusId": "3023",
                        "BefizetesMegerkezett": "Igen",
                        "DijbekeroUzenetek": adatlap.DijbekeroUzenetek
                        + f"\nBefizetés megérkezett Számlázz.hu-n keresztül: {datetime.datetime.now()}",
                    },
                )
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


main()
