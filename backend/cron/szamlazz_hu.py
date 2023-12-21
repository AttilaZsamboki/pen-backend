from ..utils.minicrm import (
    contact_details,
    billing_address,
    update_adatlap_fields,
)
from ..utils.logs import log
import requests
import datetime
import os
import time
from dotenv import load_dotenv
from ..models import MiniCrmAdatlapok
import traceback

load_dotenv()

SZAMLA_AGENT_KULCS = os.environ.get("SZAMLA_AGENT_KULCS")
ENVIRONMENT = os.environ.get("ENVIRONMENT")


def create_invoice_or_proform(
    messages_field="",
    update_data=None,
    note_field="",
    payment_method_field="",
    proform_number_field="",
    status_id="",
    cash=False,
    proform=False,
    zip_field="",
    city_field="",
    address_field="",
    calc_net_price=None,
    type="",
):
    if proform:
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

    log(
        f"{name} készítésének futtatása",
        "INFO",
        f"pen_{script_name}_{type}",
    )

    def criteria(adatlap):
        if payment_method_field and (
            (not cash and adatlap[payment_method_field] != "Átutalás")
            or (cash and adatlap[payment_method_field] == "Átutalás")
        ):
            return False
        elif cash and adatlap[proform_number_field] != "":
            return False
        elif not cash and not proform and adatlap[proform_number_field] == "":
            log(
                "Nincs díjbekérő száma",
                "FAILED",
                f"pen_{name['script_name']}_{type}",
                f"adatlap: {adatlap['Id']}",
            )
            return
        return True

    adatlapok = [
        i
        for i in MiniCrmAdatlapok.objects.filter(
            StatusId=status_id,
        ).values()
        if criteria(i)
    ]
    if adatlapok == []:
        log(f"Nincs új {name}", "INFO", f"pen_{script_name}_{type}")
        return
    for adatlap in adatlapok:
        try:
            log(
                "Új adatlap",
                "INFO",
                f"pen_{script_name}_{type}",
                f"adatlap: {adatlap['Id']}",
            )
        except Exception as e:
            log(
                "Hiba akadt az adatlapok lekérdezése során",
                "ERROR",
                f"pen_{script_name}_{type}",
                f"error: {e}. adatlap: {adatlap['Id']}. adatlapok: {adatlapok}",
            )
        try:
            query_xml = f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <xmlszamlaxml xmlns="http://www.szamlazz.hu/xmlszamlaxml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.szamlazz.hu/xmlszamlaxml https://www.szamlazz.hu/szamla/docs/xsds/agentxml/xmlszamlaxml.xsd">
                    <szamlaagentkulcs>{SZAMLA_AGENT_KULCS}</szamlaagentkulcs>
                    <rendelesSzam>{adatlap["Id"]}</rendelesSzam>
                </xmlszamlaxml>
            """.strip()
            query_response = requests.post(
                "https://www.szamlazz.hu/szamla/",
                files={"action-szamla_agent_xml": ("invoice.xml", query_xml)},
            )
            if "szlahu_szamlaszam" in query_response.headers.keys():
                if (
                    proform
                    or query_response.headers["szlahu_szamlaszam"][0] == "E"
                    or cash
                ):
                    log(
                        f"Már létezik {name}",
                        "INFO",
                        f"pen_{script_name}_{type}",
                        f"adatlap: {adatlap['Id']}",
                    )
                    update_adatlap_fields(
                        adatlap["Id"],
                        {
                            messages_field: f"{name.capitalize()} készítése sikertelen volt: Már létezik {name}"
                        },
                    )
                    continue
            business_contact_id = adatlap["MainContactId"]
            business_contact = contact_details(business_contact_id)["response"]
            contact = contact_details(adatlap["ContactId"])["response"]
            address = billing_address(business_contact_id)
            if address is None:
                log(
                    "Nincsenek számlázási adatok",
                    "FAILED",
                    f"pen_{script_name}_{type}",
                )

            if business_contact is None or address is None:
                log(
                    "Nincsenek számlázási adatok",
                    "FAILED",
                    f"pen_{script_name}_{type}",
                    f"adatlap: {adatlap['Id']}",
                )
                continue
            if None in [
                business_contact.get("Name"),
                address.get("PostalCode"),
                address.get("City"),
                address.get("Address"),
                contact.get("Email"),
                business_contact.get("VatNumber"),
                adatlap.get("Name"),
                adatlap.get(zip_field),
                adatlap.get(city_field),
                adatlap.get(address_field),
                adatlap.get("Id"),
                contact.get("Phone"),
            ]:
                log(
                    "Nincsenek számlázási adatok",
                    "FAILED",
                    f"pen_{script_name}_{type}",
                    f"adatlap: {adatlap['Id']}",
                )
                continue

            net_price = calc_net_price(adatlap)
            if not net_price:
                log("Nincs nettó ár", "FAILED", f"pen_{script_name}_{type}")
                return
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
                    <megjegyzes><![CDATA[{adatlap[note_field] if proform else adatlap[note_field]}]]></megjegyzes>
                    <rendelesSzam>{adatlap["Id"]}</rendelesSzam>
                    <!-- order number -->
                    <dijbekeroSzamlaszam>{adatlap[proform_number_field]}</dijbekeroSzamlaszam>
                    <!-- reference to pro forma invoice number -->
                    <vegszamla>false</vegszamla>
                    <!-- invoice (after a deposit invoice) -->
                    <dijbekero>{'true' if proform else 'false'}</dijbekero>
                    <!-- proform invoice -->
                    <szamlaszamElotag>{"TMTSZ" if ENVIRONMENT == "production" else "ERP"}</szamlaszamElotag>
                    <!-- One of the prefixes from the invoice pad menu  -->
                </fejlec>
                <elado>
                    <!-- Details of the merchant-->
                    <bank>OTP</bank>
                    <!-- bank name -->
                    <bankszamlaszam>11741055-20013712</bankszamlaszam>
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
                    <nev><![CDATA[{business_contact["Name"]}]]></nev>
                    <!-- name -->
                    <irsz><![CDATA[{address["PostalCode"]}]]></irsz>
                    <!-- ZIP code -->
                    <telepules><![CDATA[{address["City"]}]]></telepules>
                    <!-- city -->
                    <cim><![CDATA[{address["Address"]}]]></cim>
                    <!-- address -->
                    <email><![CDATA[{contact["Email"]}]]></email>
                    <!-- should we send the e-mail to the customer (by email) -->
                    <adoszam>{business_contact["VatNumber"]}</adoszam>
                    <!-- fiscal number/tax number -->
                    <postazasiNev><![CDATA[{adatlap["Name"]}]]></postazasiNev>
                    <!--delivery name/postal name -->
                    <postazasiIrsz>{adatlap[zip_field]}</postazasiIrsz>
                    <!--delivery ZIP code/postal ZIP code -->
                    <postazasiTelepules><![CDATA[{adatlap[city_field]}]]></postazasiTelepules>
                    <!--delivery city/postal city -->
                    <postazasiCim><![CDATA[{adatlap[address_field]}]]></postazasiCim>
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
                        <nettoEgysegar>{net_price}</nettoEgysegar>
                        <afakulcs>27</afakulcs>
                        <nettoErtek>{net_price}</nettoErtek>
                        <afaErtek>{net_price * 0.27}</afaErtek>
                        <bruttoErtek>{net_price * 1.27}</bruttoErtek>
                    </tetel>
                </tetelek>
            </xmlszamla>
            """
            if ENVIRONMENT == "production":
                from ..config_production import base_path
            else:
                from ..config_development import base_path

            invoice_path = f"{base_path}/static/invoice.xml"
            with open(invoice_path, "w", encoding="utf-8") as f:
                f.write(xml)
                f.close()

            url = "https://www.szamlazz.hu/szamla/"
            response = requests.post(
                url, files={"action-xmlagentxmlfile": open(invoice_path, "rb")}
            )
            try:
                szamlaszam = response.headers["szlahu_szamlaszam"]
            except:
                update_resp = update_adatlap_fields(
                    adatlap["Id"],
                    {
                        messages_field: f"{name.capitalize()} készítése sikertelen volt: {response.text[:800]}"
                    },
                )
                log(
                    f"{name.capitalize()} készítése sikertelen volt",
                    "ERROR",
                    f"pen_{script_name}_{type}",
                    f"adatlap: {adatlap['Id']}, error: {response.text}",
                )
                continue
            if ENVIRONMENT == "production":
                os.remove(invoice_path)
            pdf_path = f"{base_path}/static/{szamlaszam}.pdf"
            with open(pdf_path, "wb") as f:
                f.write(response.content)
                f.close()
            for _ in range(2):
                update_resp = update_adatlap_fields(
                    adatlap["Id"],
                    update_data(proform, name, adatlap, szamlaszam),
                )
                if update_resp["code"] == 400:
                    log(
                        f"Hiba akadt a {name} feltöltésében",
                        "ERROR",
                        script_name=f"pen_{script_name}_{type}",
                        details=f"adatlap: {adatlap['Id']}, error: {update_resp['reason']}",
                    )
                    time.sleep(180)
                else:
                    break

            if ENVIRONMENT == "production":
                os.remove(pdf_path)
        except KeyError as e:
            log(
                "ERROR",
                "FAILED",
                script_name=f"pen_{script_name}_{type}",
                details=traceback.format_exc(),
            )
            continue
        except Exception as e:
            log(
                f"Hiba akadt a {name} feltöltésében",
                "ERROR",
                script_name=f"pen_{script_name}_{type}",
                details=traceback.format_exc(),
            )
            continue
        log(
            f"{name.capitalize()}k feltöltése sikeres",
            "SUCCESS",
            script_name=f"pen_{script_name}_{type}",
        )
        continue


def update_data_garancia(proform, name: str, adatlap, szamlaszam):
    return {
        "DijbekeroPdf3"
        if proform
        else "SzamlaPdf2": f"https://pen.dataupload.xyz/static/{szamlaszam}.pdf",
        "StatusId": "Utalásra vár" if proform else adatlap["StatusId"],
        "DijbekeroSzama3" if proform else "SzamlaSorszama": szamlaszam,
        f"KiallitasDatuma{'3' if proform else '4'}": datetime.datetime.now().strftime(
            "%Y-%m-%d"
        ),
        "FizetesiHatarido2": (
            datetime.datetime.now() + datetime.timedelta(days=3)
        ).strftime("%Y-%m-%d")
        if proform
        else adatlap["FizetesiHatarido2"],
        (
            "DijbekeroUzenetek2" if proform else "SzamlaUzenetek2"
        ): f"{name.capitalize()} elkészült {datetime.datetime.now()}",
    }


def update_data_felmeres(proform, name: str, adatlap, szamlaszam):
    return {
        "DijbekeroPdf2"
        if proform
        else "SzamlaPdf": f"https://pen.dataupload.xyz/static/{szamlaszam}.pdf",
        "StatusId": "Utalásra vár" if proform else adatlap["StatusId"],
        "DijbekeroSzama2" if proform else "SzamlaSorszama2": szamlaszam,
        f"KiallitasDatuma{'' if proform else '2'}": datetime.datetime.now().strftime(
            "%Y-%m-%d"
        ),
        "FizetesiHatarido": (
            datetime.datetime.now() + datetime.timedelta(days=3)
        ).strftime("%Y-%m-%d")
        if proform
        else adatlap["FizetesiHatarido"],
        (
            "DijbekeroUzenetek" if proform else "SzamlaUzenetek"
        ): f"{name.capitalize()} elkészült {datetime.datetime.now()}",
    }


# Felmérés
data = {
    "city_field": "Telepules",
    "payment_method_field": "FizetesiMod2",
    "update_data": update_data_felmeres,
    "zip_field": "Iranyitoszam",
    "address_field": "Cim2",
    "calc_net_price": lambda adatlap: adatlap["FelmeresiDij"],
    "proform_number_field": "DijbekeroSzama2",
    "type": "felmeres",
}
create_invoice_or_proform(
    status_id=3086,
    proform=False,
    cash=True,
    messages_field="SzamlaUzenetek",
    note_field="SzamlaMegjegyzes",
    **data,
)
create_invoice_or_proform(
    status_id=3023,
    proform=False,
    cash=False,
    messages_field="SzamlaUzenetek",
    note_field="SzamlaMegjegyzes",
    **data,
)
create_invoice_or_proform(
    status_id=3079,
    proform=True,
    cash=False,
    messages_field="DijbekeroUzenetek",
    note_field="DijbekeroMegjegyzes2",
    **data,
)


# Garancia
def calc_net_price(adatlap):
    if adatlap["BejelentesTipusa"] == "Rendszergarancia":
        return adatlap["NettoFelmeresiDij"]
    elif adatlap["BejelentesTipusa"] == "Karbantartás":
        return adatlap["NettoFelmeresiDij"] + (
            adatlap["KarbantartasNettoDij"] if adatlap["KarbantartasNettoDij"] else 0
        )
    return None


data = {
    "city_field": "Telepules2",
    "update_data": update_data_garancia,
    "zip_field": "Iranyitoszam2",
    "address_field": "Cim3",
    "calc_net_price": calc_net_price,
    "proform_number_field": "DijbekeroSzama3",
    "type": "garancia",
}
create_invoice_or_proform(
    status_id=3129,
    proform=False,
    cash=False,
    messages_field="SzamlaUzenetek2",
    note_field="SzamlaMegjegyzes2",
    **data,
)
create_invoice_or_proform(
    status_id=3127,
    proform=True,
    cash=False,
    messages_field="DijbekeroUzenetek2",
    note_field="DijbekeroMegjegyzes3",
    **data,
)
