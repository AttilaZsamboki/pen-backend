import os
from ..utils.logs import log
from ..models import MiniCrmAdatlapok
import requests
from dotenv import load_dotenv
from ..utils.minicrm import (
    update_adatlap_fields,
)

load_dotenv()

SZAMLA_AGENT_KULCS = os.environ.get("SZAMLA_AGENT_KULCS")
TESZT_SZAMLA_AGENT_KULCS = os.environ.get("TESZT_SZAMLA_AGENT_KULCS")


class InvoiceCheck:
    def __init__(
        self,
        test=False,
        def_criteria=lambda _: True,
        update_adatlap=lambda _: None,
        name="",
    ):
        self.test = test
        self.def_criteria = def_criteria
        self.update_adatlap = update_adatlap
        self.name = name


def main(invoice_check: InvoiceCheck):
    script_name = "pen_check_invoice" + "_" + invoice_check.name
    log("Szamlazz.hu számla ellenőrzés", "INFO", script_name=script_name)
    adatlapok = [
        i
        for i in MiniCrmAdatlapok.objects.filter(Deleted="0")
        if invoice_check.def_criteria(i)
    ]
    for adatlap in adatlapok:
        log(
            "Szamlazz.hu számla ellenőrzés",
            "INFO",
            script_name=script_name,
            details=f"adatlap: {adatlap.Id}",
        )
        query_xml = f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <xmlszamlaxml xmlns="http://www.szamlazz.hu/xmlszamlaxml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.szamlazz.hu/xmlszamlaxml https://www.szamlazz.hu/szamla/docs/xsds/agentxml/xmlszamlaxml.xsd">
            <szamlaagentkulcs>{SZAMLA_AGENT_KULCS if not invoice_check.test else TESZT_SZAMLA_AGENT_KULCS}</szamlaagentkulcs>
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
                update_data = invoice_check.update_adatlap(adatlap, szamlaszam)
                update_resp = update_adatlap_fields(
                    adatlap.Id,
                    update_data,
                )
                if update_resp["code"] == 200:
                    log(
                        "Számlaszám feltöltve",
                        "INFO",
                        script_name=script_name,
                        details=f"adatlap: {adatlap.Id}, szamlaszam: {szamlaszam}",
                    )
                    continue
                log(
                    f"Hiba akadt a számlaszám feltöltésében",
                    "ERROR",
                    script_name=script_name,
                    details=f"adatlap: {adatlap.Id}, error: {update_resp['reason']}",
                    data=update_data,
                )
                continue
            log(
                "Nincs számla",
                "INFO",
                script_name=script_name,
                details=f"adatlap: {adatlap.Id}",
            )
            continue
        log(
            "Nincs díjbekérő",
            "INFO",
            script_name=script_name,
            details=f"adatlap: {adatlap.Id}",
        )


def update_data_felmeres(_: MiniCrmAdatlapok, szamlaszam):
    return {
        "SzamlaSorszama2": szamlaszam,
    }


main(
    InvoiceCheck(
        test=True,
        def_criteria=lambda adatlap: adatlap.StatusId == 3023
        and not (adatlap.SzamlaSorszama2 and adatlap.SzamlaSorszama2 != ""),
        update_adatlap=update_data_felmeres,
        name="felmeres",
    )
)
