from .minicrm import get_all_adatlap, adatlap_details, contact_details, billing_address, update_adatlap_fields
from .logs import log
import requests
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

SZAMLA_AGENT_KULCS = os.environ.get("SZAMLA_AGENT_KULCS")
API_KEY = os.environ.get("PEN_MINICRM_API_KEY")
SYSTEM_ID = os.environ.get("PEN_MINICRM_SYSTEM_ID")
environment = os.environ.get("ENVIRONMENT")


def dijbekero():
    log("Díjbekérő futtatása", "INFO", "pen_dijbekero")
    try:
        adatlapok = get_all_adatlap(23, 3079)
        adatlapok = adatlapok["Results"]
        if adatlapok == []:
            return
        for i in adatlapok.keys():
            adatlap = adatlap_details(adatlapok[i]["Id"])
            if adatlap["FizetesiMod2"] != "Átutalás":
                return
            contact_id = adatlapok[i]["BusinessId"]
            contact = contact_details(contact_id)
            address = billing_address(contact_id)

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
                    <megjegyzes>{adatlap["DijbekeroMegjegyzes2"]}</megjegyzes>
                    <rendelesSzam>{adatlap["Id"]}</rendelesSzam>
                    <!-- order number -->
                    <dijbekeroSzamlaszam>{adatlap["DijbekeroSzama2"]}</dijbekeroSzamlaszam>
                    <!-- reference to pro forma invoice number -->
                    <vegszamla>false</vegszamla>
                    <!-- invoice (after a deposit invoice) -->
                    <dijbekero>true</dijbekero>
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
            if environment == 'production':
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
            os.remove(invoice_path)
            dijbekero_number = response.headers["szlahu_szamlaszam"]
            pdf_path = f"{base_path}/static/{dijbekero_number}.pdf"
            with open(pdf_path, "wb") as f:
                f.write(response.content)
                f.close()
            update_adatlap_fields(adatlap["Id"], {
                "DijbekeroPdf2": f"http://pen.dataupload.xyz/static/{dijbekero_number}.pdf", "StatusId": "Utalásra vár", "DijbekeroSzama2": dijbekero_number, "KiallitasDatuma": datetime.datetime.now().strftime("%Y-%m-%d"), "FizetesiHatarido": (datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%Y-%m-%d"), "DijbekeroUzenetek": f"Díjbekéro elkészült {datetime.datetime.now()}"})
            os.remove(pdf_path)
            log("Díjbekérők feltöltése sikeres",
                "SUCCESS", script_name="pen_dijbekero")
            return "Success"
    except KeyError as e:
        log("Nincsenek számlázási adatok", "FAILED",
            script_name="pen_dijbekero", details=e)
        return "Error"
    except Exception as e:
        log("Hiba akadt a díjbekérő feltöltésében", "ERROR",
            script_name="pen_dijbekero", details=e)
        return "Error"

dijbekero()