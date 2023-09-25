from ..utils.minicrm import get_all_adatlap_details, contact_details, billing_address, update_adatlap_fields, statuses
from ..utils.logs import log
import requests
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

SZAMLA_AGENT_KULCS = os.environ.get("SZAMLA_AGENT_KULCS")
ENVIRONMENT = os.environ.get("ENVIRONMENT")


def create_invoice_or_proform(is_proform=True, cash=False):
    if is_proform:
        name = "díjbekérő"
        script_name = "proform"
    else:
        if cash:
            name = "készpénzes számla"
            script_name = "cash_invoice"
        else:
            name = "számla"
            script_name = "invoice"
    log(f"{name.capitalize()} készítésének futtatása", "INFO", f"pen_{script_name}")
    status_id = 0
    if cash:
        status_id = statuses["Felmérés"]["Sikeres felmérés"]
    elif is_proform:
        status_id = 3079
    else:
        status_id = 3023

    def criteria(adatlap):
        if adatlap["Deleted"] == 1:
            return False
        elif (not cash and adatlap["FizetesiMod2"] != "Átutalás") or (cash and adatlap["FizetesiMod2"] == "Átutalás"):
            return False
        elif cash and adatlap["DijbekeroSzama2"] != "":
            return False
        elif not cash and not is_proform and adatlap["DijbekeroSzama2"] == "":
            log("Nincs díjbekérő száma", "FAILED", f"pen_{script_name}", f"adatlap: {adatlap['Id']}")
            return
        return True

    adatlapok = get_all_adatlap_details(23, status_id, criteria=criteria)
    if adatlapok == []:
        log(f"Nincs új {name}", "INFO", f"pen_{script_name}")
        return
    for adatlap in adatlapok:
        try:
            query_xml = f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <xmlszamlaxml xmlns="http://www.szamlazz.hu/xmlszamlaxml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.szamlazz.hu/xmlszamlaxml https://www.szamlazz.hu/szamla/docs/xsds/agentxml/xmlszamlaxml.xsd">
                    <szamlaagentkulcs>{SZAMLA_AGENT_KULCS}</szamlaagentkulcs>
                    <rendelesSzam>{adatlap["Id"]}</rendelesSzam>
                </xmlszamlaxml>
            """.strip()
            query_response = requests.post("https://www.szamlazz.hu/szamla/", files={"action-szamla_agent_xml": ("invoice.xml", query_xml)})
            if "szlahu_szamlaszam" in query_response.headers.keys():
                if is_proform or query_response.headers["szlahu_szamlaszam"][0] == "E" or cash:
                    log(f"Már létezik {name}", "INFO", f"pen_{script_name}", f"adatlap: {adatlap['Id']}")
                    continue
            contact_id = adatlap["BusinessId"]
            contact = contact_details(contact_id)["response"]
            address = billing_address(contact_id)

            if contact is None or address is None:
                log("Nincsenek számlázási adatok", "FAILED", f"pen_{script_name}", f"adatlap: {adatlap['Id']}")
                continue
            if None in [contact.get("Name"), address.get("PostalCode"), address.get("City"), address.get("Address"), contact.get("Email"), contact.get("VatNumber"), adatlap.get("Name"), adatlap.get("Iranyitoszam"), adatlap.get("Telepules"), adatlap.get("Cim2"), adatlap.get("Id"), contact.get("Phone")]:
                log("Nincsenek számlázási adatok", "FAILED", f"pen_{script_name}", f"adatlap: {adatlap['Id']}")
                continue

            xml = f"""<?xml version="1.0" encoding="UTF-8"?>
            <xmlszamla xmlns="http://www.szamlazz.hu/xmlszamla" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.szamlazz.hu/xmlszamla https://www.szamlazz.hu/szamla/docs/xsds/agent/xmlszamla.xsd">
                <beallitasok>
                    <szamlaagentkulcs>{SZAMLA_AGENT_KULCS}</szamlaagentkulcs>
                    <eszamla>true</eszamla>
                    <szamlaLetoltes>true</szamlaLetoltes>
                </beallitasok>
                <fejlec>
                    <!-- header -->
                    <keltDatum>{datetime.datetime.now().strftime("%Y-%m-%d")}</keltDatum>
                    <teljesitesDatum>{datetime.datetime.now().strftime("%Y-%m-%d")}</teljesitesDatum>
                    <!-- creating date, in this exact format -->
                    <fizetesiHataridoDatum>{(datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%Y-%m-%d")}</fizetesiHataridoDatum>
                    <!-- due date -->
                    <fizmod>Átutalás</fizmod>
                    <!-- payment type: it can be seen in case you create the invoice
                                                    from browser -->
                    <penznem>HUF</penznem>
                    <!-- currency: it can be seen in case you create the invoice
                                                    from browser -->
                    <szamlaNyelve>hu</szamlaNyelve>
                    <!-- language of invoice, can  be: de, en, it, hu, fr, ro, sk, hr
                                                    -->
                    <megjegyzes>{adatlap["DijbekeroMegjegyzes2"] if is_proform else adatlap["SzamlaMegjegyzes"]}</megjegyzes>
                    <rendelesSzam>{adatlap["Id"]}</rendelesSzam>
                    <!-- order number -->
                    <dijbekeroSzamlaszam>{adatlap["DijbekeroSzama2"]}</dijbekeroSzamlaszam>
                    <!-- reference to pro forma invoice number -->
                    <vegszamla>false</vegszamla>
                    <!-- invoice (after a deposit invoice) -->
                    <dijbekero>{'true' if is_proform else 'false'}</dijbekero>
                    <!-- proform invoice -->
                    <szamlaszamElotag>KLCSR</szamlaszamElotag>
                    <!-- One of the prefixes from the invoice pad menu  -->
                </fejlec>
                <elado>
                    <!-- Details of the merchant-->
                    <bank>BB</bank>
                    <!-- bank name -->
                    <bankszamlaszam>12345678-12345678-12345678</bankszamlaszam>
                    <!-- bank account -->
                    <emailReplyto>zsamboki.attila.jr@gmail.com</emailReplyto>
                    <!-- reply e-mail address -->
                    <emailTargy>Invoice notification</emailTargy>
                    <!-- e-mail subject -->
                    <emailSzoveg>mail text</emailSzoveg>
                    <!-- text of e-mail -->
                </elado>
                <vevo>
                    <!--Buyer details -->
                    <nev>{contact["Name"]}</nev>
                    <!-- name -->
                    <irsz>{address["PostalCode"]}</irsz>
                    <!-- ZIP code -->
                    <telepules>{address["City"]}</telepules>
                    <!-- city -->
                    <cim>{address["Address"]}</cim>
                    <!-- address -->
                    <email>{contact["Email"]}</email>
                    <!-- e-mail address, if given, we will send the invoice to this mail address -->
                    <sendEmail>false</sendEmail>
                    <!-- should we send the e-mail to the customer (by email) -->
                    <adoszam>{contact["VatNumber"]}</adoszam>
                    <!-- fiscal number/tax number -->
                    <postazasiNev>{adatlap["Name"]}</postazasiNev>
                    <!--delivery name/postal name -->
                    <postazasiIrsz>{adatlap["Iranyitoszam"]}</postazasiIrsz>
                    <!--delivery ZIP code/postal ZIP code -->
                    <postazasiTelepules>{adatlap["Telepules"]}</postazasiTelepules>
                    <!--delivery city/postal city -->
                    <postazasiCim>{adatlap["Cim2"]}</postazasiCim>
                    <!--delivery address/postal address -->
                    <azonosito>{adatlap["Id"]}</azonosito>
                    <!-- identification -->
                    <telefonszam>{contact["Phone"]}</telefonszam>
                    <!-- phone number -->
                </vevo>
                <tetelek>
                    <!-- items on invoice -->
                    <tetel>
                        <!-- item 2, details are same as above -->
                        <megnevezes>Felmérés</megnevezes>
                        <mennyiseg>1.0</mennyiseg>
                        <mennyisegiEgyseg>db</mennyisegiEgyseg>
                        <nettoEgysegar>{adatlap["FelmeresiDij"]}</nettoEgysegar>
                        <afakulcs>27</afakulcs>
                        <nettoErtek>{adatlap["FelmeresiDij"]}</nettoErtek>
                        <afaErtek>{adatlap["FelmeresiDij"] * 0.27}</afaErtek>
                        <bruttoErtek>{adatlap["FelmeresiDij"] * 1.27}</bruttoErtek>
                    </tetel>
                </tetelek>
            </xmlszamla>
            """
            if ENVIRONMENT == 'production':
                from ..config_production import base_path
            else:
                from ..config_development import base_path

            invoice_path = f"{base_path}/static/invoice.xml"
            with open(invoice_path, "w", encoding="utf-8") as f:
                f.write(xml)
                f.close()

            url = "https://www.szamlazz.hu/szamla/"
            response = requests.post(
                url, files={"action-xmlagentxmlfile": open(invoice_path, "rb")})
            if response.status_code != 200:
                update_resp = update_adatlap_fields(adatlap["Id"], {
                    "DijbekeroUzenetek" if is_proform else "SzamlaUzenetek": f"{name.capitalize()} készítése sikertelen volt: {response.text}"})
                log(f"{name.capitalize()} készítése sikertelen volt: {response.text}", "ERROR", f"pen_{script_name}", f"adatlap: {adatlap['Id']}, error: {response.text}")
                continue
            os.remove(invoice_path)
            szamlaszam = response.headers["szlahu_szamlaszam"]
            pdf_path = f"{base_path}/static/{szamlaszam}.pdf"
            with open(pdf_path, "wb") as f:
                f.write(response.content)
                f.close()
            update_resp = update_adatlap_fields(adatlap["Id"], {
                "DijbekeroPdf2" if is_proform else "SzamlaPdf": f"https://pen.dataupload.xyz/static/{szamlaszam}.pdf", "StatusId": "Utalásra vár" if is_proform else adatlap["StatusId"], "DijbekeroSzama2" if is_proform else "SzamlaSorszama2": szamlaszam, f"KiallitasDatuma{'' if is_proform else '2'}": datetime.datetime.now().strftime("%Y-%m-%d"), "FizetesiHatarido": (datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%Y-%m-%d") if is_proform else adatlap["FizetesiHatarido"], "DijbekeroUzenetek" if is_proform else "SzamlaUzenetek": f"{name.capitalize()} elkészült {datetime.datetime.now()}"})
            if update_resp["code"] == 400:
                log(f"Hiba akadt a {name} feltöltésében", "ERROR", script_name=f"pen_{script_name}", details=f"adatlap: {adatlap['Id']}, error: {update_resp['reason']}")
            os.remove(pdf_path)
        except KeyError as e:
            log("Nincsenek számlázási adatok", "FAILED",
                script_name=f"pen_{script_name}", details=f"adatlap: {adatlap['Id']}, error: {e}")
            continue
        except Exception as e:
            log(f"Hiba akadt a {name} feltöltésében", "ERROR",
                script_name=f"pen_{script_name}", details=f"error:{e}")
            continue
        log(f"{name.capitalize()}k feltöltése sikeres",
            "SUCCESS", script_name=f"pen_{script_name}")
        continue

create_invoice_or_proform(is_proform=False)
create_invoice_or_proform(is_proform=True)
create_invoice_or_proform(is_proform=False, cash=True)