import os
from functools import partial

import requests
from dotenv import load_dotenv

from ..utils.logs import log as l
from ..models import MiniCrmAdatlapok
from ..utils.minicrm import MiniCrmClient

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
    minicrm_client = MiniCrmClient(script_name=script_name)
    log = partial(l, script_name=script_name)

    log("Szamlazz.hu számla ellenőrzés", "INFO")
    adatlapok = [
        i
        for i in MiniCrmAdatlapok.objects.filter(Deleted="0")
        if invoice_check.def_criteria(i)
    ]
    for adatlap in adatlapok:
        log(
            "Szamlazz.hu számla ellenőrzés",
            "INFO",
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
        print(adatlap.Id)
        print(query_response.headers.keys())
        if "szlahu_szamlaszam" in query_response.headers.keys():
            szamlaszam = query_response.headers["szlahu_szamlaszam"]
            if szamlaszam[0] == "E":
                update_data = invoice_check.update_adatlap(adatlap, szamlaszam)
                update_resp = minicrm_client.update_adatlap_fields(
                    adatlap.Id,
                    update_data,
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
                    data=update_data,
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


main(
    InvoiceCheck(
        test=False,
        def_criteria=lambda adatlap: adatlap.StatusId == 3023
        and not (adatlap.SzamlaSorszama2 and adatlap.SzamlaSorszama2 != ""),
        update_adatlap=update_data_felmeres,
        name="felmeres",
    )
)
