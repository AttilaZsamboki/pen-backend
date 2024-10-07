from ..utils.logs import log  # noqa
import datetime
import traceback
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import requests

from ..models import MiniCrmAdatlapok, Systems
from ..services.minicrm import MiniCRMWrapper


@dataclass
class Input:
    StatusId: str
    CategoryId: str
    UpdateAdatlap: callable


class Main(MiniCRMWrapper):
    script_name = "pen_paid_invoice"

    def fn(self, input: Input):
        self.log(
            "Kifizetettt számlák csekkolása megkezdődött",
            status="INFO",
        )

        for adatlap in self.get_adatlapok(
            StatusIdStr=input.StatusId, CategoryIdStr=input.CategoryId
        ):
            query_xml = f"""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <xmlszamlaxml xmlns="http://www.szamlazz.hu/xmlszamlaxml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.szamlazz.hu/xmlszamlaxml https://www.szamlazz.hu/szamla/docs/xsds/agentxml/xmlszamlaxml.xsd">
                    <szamlaagentkulcs>{self.system.szamla_agent_kulcs}</szamlaagentkulcs>
                        <rendelesSzam>{adatlap.Id}</rendelesSzam>
                    </xmlszamlaxml>
                """.strip()
            query_response = requests.post(
                "https://www.szamlazz.hu/szamla/",
                files={"action-szamla_agent_xml": ("invoice.xml", query_xml)},
            )
            if query_response.status_code != 200:
                self.log(
                    "Számla lekérdezése sikertelen",
                    status="ERROR",
                    details=query_response.reason,
                )
                continue

            root = ET.fromstring(query_response.text)

            ns = {"szamla": "http://www.szamlazz.hu/szamla"}

            brutto = root.find(".//szamla:brutto", ns)
            osszeg = root.find(".//szamla:osszeg", ns)

            if osszeg is not None and brutto is not None:
                if brutto.text == osszeg.text:
                    self.log(
                        "Kifizetett számla",
                        status="INFO",
                        details="Adatlap ID: " + str(adatlap.Id),
                    )
                    resp = self.minicrm_client.update_adatlap_fields(
                        adatlap.Id, input.UpdateAdatlap(adatlap)
                    )
                    if resp["code"] == 200:
                        self.log(
                            "Adatlap frissítve",
                            status="INFO",
                            details="Adatlap ID: " + str(adatlap.Id),
                        )
                    else:
                        self.log(
                            "Adatlap frissítése sikertelen",
                            status="ERROR",
                            details=resp["reason"],
                        )

    def main(self):
        modules = [
            Input(
                StatusId="Utalásra vár",
                UpdateAdatlap=self.update_felmeres_adatlap,
                CategoryId="Felmérés",
            ),
            Input(
                StatusId="UTALÁSRA VÁR",
                UpdateAdatlap=self.update_garancia_adatlap,
                CategoryId="Ügyfélkapu",
            ),
        ]
        for i in modules:
            self.main(i)

    def update_felmeres_adatlap(self, adatlap: MiniCrmAdatlapok):
        status_id = self.get_setting(label="Felmérésre vár", type="StatusId").value
        return {
            "StatusId": status_id,
            "BefizetesMegerkezett": "Igen",
            "DijbekeroUzenetek": (
                adatlap.DijbekeroUzenetek
                if adatlap.DijbekeroUzenetek
                else ""
                + f"\nBefizetés megérkezett Számlázz.hu-n keresztül: {datetime.datetime.now()}"
            ),
        }

    def update_garancia_adatlap(self, adatlap: MiniCrmAdatlapok):
        status_id = self.get_setting(label="KISZÁLLÁSRA VÁR", type="StatusId").value
        return {
            "StatusId": status_id,
            "BefizetesMegerkezett2": "Igen",
            "DijbekeroUzenetek2": (
                adatlap.DijbekeroUzenetek if adatlap.DijbekeroUzenetek else ""
            )
            + f"\nBefizetés megérkezett Számlázz.hu-n keresztül: {datetime.datetime.now()}",
        }


if __name__ == "__main__":
    try:
        for system in Systems.objects.all():
            Main(system=system).main()
    except Exception as e:
        log(
            "Kifizetett számlák csekkolása sikertelen",
            script_name="pen_paid_invoice",
            status="FAILED",
            details=traceback.format_exc(),
        )
