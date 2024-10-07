import datetime
import os
import time
import traceback

import requests
from dotenv import load_dotenv

from ..models import MiniCrmAdatlapok, Systems
from ..services.minicrm import MiniCRMWrapper
from ..utils.minicrm import Address
from dataclasses import dataclass

load_dotenv()

ENVIRONMENT = os.environ.get("ENVIRONMENT")


class Main(MiniCRMWrapper):
    def create_invoice_or_proform(
        self,
        messages_field="",
        update_data=None,
        note_field="",
        payment_method_field="",
        proform_number_field="",
        cash=False,
        proform=False,
        zip_field="",
        city_field="",
        address_field="",
        calc_net_price=None,
        type_name="",
        test=False,
        criteria=lambda _: True,
        payment_deadline=lambda _: (
            datetime.datetime.now() + datetime.timedelta(days=3)
        ).strftime("%Y-%m-%d"),
        prefix="TMTSZ",
        items=None,
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
        self.script_name = f"pen_{script_name}_{type_name}"
        self.log(f"{name.capitalize()} készítésének futtatása", "INFO")

        def def_criteria(adatlap: MiniCrmAdatlapok):
            if criteria(adatlap):
                if payment_method_field and (
                    (not cash and adatlap.__dict__[payment_method_field] != "Átutalás")
                    or (cash and adatlap.__dict__[payment_method_field] == "Átutalás")
                ):
                    self.log(
                        "Nem megfelelő fizetési mód",
                        "FAILED",
                    )
                    return False
                elif (
                    (cash or proform)
                    and adatlap.__dict__[proform_number_field] != ""
                    and adatlap.__dict__[proform_number_field] is not None
                ):
                    self.log(
                        "Már létezik " + name,
                        "FAILED",
                        details=adatlap.Id,
                    )
                    return False
                elif (
                    not cash
                    and not proform
                    and adatlap.__dict__[proform_number_field] == ""
                ):
                    self.log(
                        "Nincs díjbekérő száma",
                        "FAILED",
                        details=f"adatlap: {adatlap.Id}",
                    )
                    return False
                return True
            else:
                return False

        adatlapok = [i for i in self.get_adatlapok(Deleted="0") if def_criteria(i)]
        if adatlapok == []:
            self.log(f"Nincs új {name}", "INFO")
            return
        for adatlap in adatlapok:
            self.log(
                "Új adatlap",
                "INFO",
                details=f"adatlap: {adatlap.Id}",
            )
            try:
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
                if "szlahu_szamlaszam" in query_response.headers.keys():
                    if (
                        proform
                        or query_response.headers["szlahu_szamlaszam"][0] == "E"
                        or cash
                    ):
                        self.log(
                            f"Már létezik {name}",
                            "INFO",
                            details=f"adatlap: {adatlap.Id}, szamlaszam: {query_response.headers['szlahu_szamlaszam']}",
                        )
                        self.minicrm_client.update_adatlap_fields(
                            adatlap.Id,
                            {
                                messages_field: f"{name.capitalize()} készítése sikertelen volt: Már létezik {name}"
                            },
                        )
                        continue
                business_contact_id = adatlap.MainContactId
                if business_contact_id is None:
                    self.log(
                        "Nincsenek számlázási adatok",
                        "FAILED",
                        f"adatlap: {adatlap.Id}",
                    )
                    continue
                business_contact = self.minicrm_client.contact_details(
                    business_contact_id
                )
                if business_contact_id != adatlap.ContactId:
                    contact = self.minicrm_client.contact_details(adatlap.ContactId)
                    address = self.minicrm_client.get_address(business_contact_id)
                if business_contact_id == adatlap.ContactId or not address:
                    contact = business_contact
                    contact.Name = (
                        contact.FirstName + " " + contact.LastName
                        if not contact.Name
                        else contact.Name
                    )
                    address = Address(
                        PostalCode=adatlap.__dict__.get(zip_field),
                        City=adatlap.__dict__.get(city_field),
                        Address=adatlap.__dict__.get(address_field),
                    )
                if address is None or type(address) == str:
                    self.log("Nincsen cím", "FAILED")
                    continue

                if business_contact is None:
                    self.log(
                        "Nincsenek adatok",
                        "FAILED",
                        f"adatlap: {adatlap.Id}",
                        business_contact,
                    )
                    continue

                if None in [
                    business_contact.Name,
                    address.get("PostalCode"),
                    address.get("City"),
                    address.get("Address"),
                    contact.Email,
                    adatlap.Id,
                    contact.Phone,
                ]:
                    self.log(
                        "Nincsenek számlázási adatok",
                        "FAILED",
                        f"adatlap: {adatlap.Id}",
                    )
                    continue

                net_price = calc_net_price(adatlap)
                if not net_price:
                    self.log("Nincs nettó ár", "FAILED")
                    continue
                xml = f"""<?xml version="1.0" encoding="UTF-8"?>
                <xmlszamla xmlns="http://www.szamlazz.hu/xmlszamla" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.szamlazz.hu/xmlszamla https://www.szamlazz.hu/szamla/docs/xsds/agent/xmlszamla.xsd">
                    <beallitasok>
                        <szamlaagentkulcs>{self.system.szamla_agent_kulcs}</szamlaagentkulcs>
                        <eszamla>true</eszamla>
                        <szamlaLetoltes>true</szamlaLetoltes>
                    </beallitasok>
                    <fejlec>
                        <!-- header -->
                        <keltDatum>{datetime.datetime.now().strftime("%Y-%m-%d")}</keltDatum>
                        <teljesitesDatum>{datetime.datetime.now().strftime("%Y-%m-%d")}</teljesitesDatum>
                        <!-- creating date, in this exact format -->
                        <fizetesiHataridoDatum>{payment_deadline(adatlap)}</fizetesiHataridoDatum>
                        <!-- due date -->
                        <fizmod>{"Átutalás" if not cash else "Készpénz"}</fizmod>
                        <!-- payment type: it can be seen in case you create the invoice
                                                        from browser -->
                        <penznem>HUF</penznem>
                        <!-- currency: it can be seen in case you create the invoice
                                                        from browser -->
                        <szamlaNyelve>hu</szamlaNyelve>
                        <!-- language of invoice, can  be: de, en, it, hu, fr, ro, sk, hr
                                                        -->
                        <megjegyzes><![CDATA[{adatlap.__dict__[note_field] if proform else adatlap.__dict__[note_field]}]]></megjegyzes>
                        <rendelesSzam>{adatlap.Id}</rendelesSzam>
                        <!-- order number -->
                        <dijbekeroSzamlaszam>{adatlap.__dict__[proform_number_field]}</dijbekeroSzamlaszam>
                        <!-- reference to pro forma invoice number -->
                        <vegszamla>false</vegszamla>
                        <!-- invoice (after a deposit invoice) -->
                        <dijbekero>{'true' if proform else 'false'}</dijbekero>
                        <!-- proform invoice -->
                        <szamlaszamElotag>{prefix if ENVIRONMENT == "production" and not test else "ERP"}</szamlaszamElotag>
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
                        <nev><![CDATA[{business_contact.Name}]]></nev>
                        <!-- name -->
                        <irsz><![CDATA[{address.PostalCode}]]></irsz>
                        <!-- ZIP code -->
                        <telepules><![CDATA[{address.City}]]></telepules>
                        <!-- city -->
                        <cim><![CDATA[{address.Address}]]></cim>
                        <!-- address -->
                        <email><![CDATA[{contact.Email}]]></email>
                        <!-- should we send the e-mail to the customer (by email) -->
                        <adoszam>{business_contact.VatNumber}</adoszam>
                        <!-- fiscal number/tax number -->
                        <azonosito>{adatlap.MainContactId}</azonosito>
                        <!-- identification -->
                        <telefonszam>{contact.Phone}</telefonszam>
                        <!-- phone number -->
                    </vevo>
                    <tetelek>
                        <!-- items on invoice -->
                        {f'''<tetel>
                            <!-- item 2, details are same as above -->
                            <megnevezes>Felmérés</megnevezes>
                            <mennyiseg>1.0</mennyiseg>
                            <mennyisegiEgyseg>db</mennyisegiEgyseg>
                            <nettoEgysegar>{net_price}</nettoEgysegar>
                            <afakulcs>27</afakulcs>
                            <nettoErtek>{net_price}</nettoErtek>
                            <afaErtek>{net_price * 0.27}</afaErtek>
                            <bruttoErtek>{net_price * 1.27}</bruttoErtek>
                        </tetel>''' if not items else items(adatlap)}
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
                if not response.ok:
                    self.log("Hiba történt a számla készítésekor", "ERROR")
                    return
                try:
                    szamlaszam = response.headers["szlahu_szamlaszam"]
                except:
                    update_resp = self.minicrm_client.update_adatlap_fields(
                        adatlap.Id,
                        {
                            messages_field: f"{name.capitalize()} készítése sikertelen volt: {response.text[:800]}"
                        },
                    )
                    self.log(
                        f"Már létezik {name}",
                        "INFO",
                        script_name,
                        response.text[:800],
                    )
                    continue
                if ENVIRONMENT == "production":
                    os.remove(invoice_path)
                pdf_path = f"{base_path}/static/{szamlaszam}.pdf"
                with open(pdf_path, "wb") as f:
                    f.write(response.content)
                    f.close()
                for _ in range(2):
                    update_request_payload = update_data(
                        proform, name, adatlap, szamlaszam
                    )
                    update_resp = self.minicrm_client.update_adatlap_fields(
                        adatlap.Id,
                        update_request_payload,
                    )
                    if update_resp["code"] == 200:
                        break
                    else:
                        self.log(
                            f"Hiba akadt a {name} feltöltésében",
                            "ERROR",
                            details=f"adatlap: {adatlap.Id}, error: {update_resp['reason']}",
                            data=update_request_payload,
                        )
                        if ENVIRONMENT == "production":
                            time.sleep(180)

                if ENVIRONMENT == "production":
                    time.sleep(60)
                    os.remove(pdf_path)
            except KeyError as e:
                self.log(
                    f"Hiba akadt a {name} készítésében",
                    "ERROR",
                    details=traceback.format_exc(),
                )
                continue
            except Exception as e:
                self.log(
                    f"Hiba akadt a {name} feltöltésében",
                    "ERROR",
                    details=traceback.format_exc(),
                )
                continue
            self.log(f"{name.capitalize()}k feltöltése sikeres", "SUCCESS")
            continue


if __name__ == "__main__":
    for system in Systems.objects.all():
        client = Main(system)

        def update_data_garancia(
            proform, name: str, adatlap: MiniCrmAdatlapok, szamlaszam
        ):
            return {
                (
                    "DijbekeroPdf3" if proform else "SzamlaPdf2"
                ): f"https://pen.dataupload.xyz/static/{szamlaszam}.pdf",
                "StatusId": "Utalásra vár" if proform else adatlap.StatusId,
                "DijbekeroSzama3" if proform else "SzamlaSorszama": szamlaszam,
                f"KiallitasDatuma{'3' if proform else '4'}": datetime.datetime.now().strftime(
                    "%Y-%m-%d"
                ),
                "FizetesiHatarido2": (
                    (datetime.datetime.now() + datetime.timedelta(days=3)).strftime(
                        "%Y-%m-%d"
                    )
                    if proform
                    else adatlap.FizetesiHatarido2.strftime("%Y-%m-%d")
                ),
                (
                    "DijbekeroUzenetek2" if proform else "SzamlaUzenetek2"
                ): f"{name.capitalize()} elkészült {datetime.datetime.now()}",
            }

        # Felmérés
        def proform_criteria(adatlap: MiniCrmAdatlapok):
            if adatlap.StatusIdStr == "Díjbekérő küldés":
                return True
            elif adatlap.StatusIdStr == "Felmérés előkészítés" and (
                (datetime.datetime.now() - adatlap.StatusUpdatedAt)
                > datetime.timedelta(days=1)
                or adatlap.SzamlazasIngatlanCimre2 == "IGEN"
            ):
                return True
            return False

        def proform_deadline(adatlap: MiniCrmAdatlapok):
            date: datetime.datetime = adatlap.FelmeresIdopontja2 - datetime.timedelta(
                days=10
            )
            if date < datetime.datetime.now():
                return (datetime.datetime.now() + datetime.timedelta(days=3)).strftime(
                    "%Y-%m-%d"
                )
            return date.strftime("%Y-%m-%d")

        def update_data_felmeres(
            self, proform, name: str, adatlap: MiniCrmAdatlapok, szamlaszam
        ):
            return {
                (
                    "DijbekeroPdf2" if proform else "SzamlaPdf"
                ): f"https://pen.dataupload.xyz/static/{szamlaszam}.pdf",
                "StatusId": "Utalásra vár" if proform else adatlap.StatusId,
                "DijbekeroSzama2" if proform else "SzamlaSorszama2": szamlaszam,
                f"KiallitasDatuma{'' if proform else '2'}": datetime.datetime.now().strftime(
                    "%Y-%m-%d"
                ),
                "FizetesiHatarido": (
                    self.proform_deadline(adatlap)
                    if proform
                    else adatlap.FizetesiHatarido
                ),
                (
                    "DijbekeroUzenetek" if proform else "SzamlaUzenetek"
                ): f"{name.capitalize()} elkészült {datetime.datetime.now()}",
            }

        data = {
            "city_field": "Telepules",
            "payment_method_field": "FizetesiMod2",
            "update_data": update_data_felmeres,
            "zip_field": "Iranyitoszam",
            "address_field": "Cim2",
            "calc_net_price": lambda adatlap: adatlap.FelmeresiDij,
            "proform_number_field": "DijbekeroSzama2",
            "type_name": "felmeres",
        }

        client.create_invoice_or_proform(
            criteria=lambda adatlap: adatlap.StatusId == 3086
            and (adatlap.SzamlaSorszama2 == "" or adatlap.SzamlaSorszama2 is None),
            proform=False,
            cash=True,
            messages_field="SzamlaUzenetek",
            note_field="SzamlaMegjegyzes",
            **data,
        )
        client.create_invoice_or_proform(
            proform=True,
            cash=False,
            criteria=proform_criteria,
            messages_field="DijbekeroUzenetek",
            note_field="DijbekeroMegjegyzes2",
            payment_deadline=proform_deadline,
            **data,
        )

        # Garancia
        def calc_net_price(adatlap: MiniCrmAdatlapok):
            if adatlap.BejelentesTipusa == "Rendszergarancia":
                return adatlap.NettoFelmeresiDij
            elif adatlap.BejelentesTipusa == "Karbantartás":
                return adatlap.NettoFelmeresiDij + (
                    adatlap.KarbantartasNettoDij if adatlap.KarbantartasNettoDij else 0
                )
            return None

        def garancia_proform_criteria(self, adatlap: MiniCrmAdatlapok):
            if adatlap.StatusId == 3126:
                if (
                    adatlap.BejelentesTipusa == "Rendszerbővítés"
                    or adatlap.FizetesiMod4 == "Készpénz"
                ):
                    resp = adatlap.change_status(3129)
                    if resp["code"] == 200:
                        self.log(
                            "Sikeresen átállítottam a státuszt a(z) {} adatlapnál.".format(
                                adatlap.Id
                            ),
                            "SUCCESS",
                            adatlap.Id,
                        )
                    else:
                        self.log(
                            "Hiba történt a(z) {} adatlapnál.".format(adatlap.Id),
                            "ERROR",
                            adatlap.Id,
                        )
                    return False
                return True
            return False

        def garancia_items(adatlap: MiniCrmAdatlapok):
            ret_str = f"""<tetel>
                                <megnevezes>Kiszállási díj</megnevezes>
                                <mennyiseg>1.0</mennyiseg>
                                <mennyisegiEgyseg>db</mennyisegiEgyseg>
                                <nettoEgysegar>{adatlap.NettoFelmeresiDij}</nettoEgysegar>
                                <afakulcs>27</afakulcs>
                                <nettoErtek>{adatlap.NettoFelmeresiDij}</nettoErtek>
                                <afaErtek>{adatlap.NettoFelmeresiDij * 0.27}</afaErtek>
                                <bruttoErtek>{adatlap.NettoFelmeresiDij * 1.27}</bruttoErtek>
                            </tetel>"""
            if adatlap.BejelentesTipusa == "Karbantartás":
                net = (
                    adatlap.KarbantartasNettoDij if adatlap.KarbantartasNettoDij else 0
                )
                ret_str += f"""<tetel>
                                <megnevezes>Karbantartási díj</megnevezes>
                                <mennyiseg>1.0</mennyiseg>
                                <mennyisegiEgyseg>db</mennyisegiEgyseg>
                                <nettoEgysegar>{net}</nettoEgysegar>
                                <afakulcs>27</afakulcs>
                                <nettoErtek>{net}</nettoErtek>
                                <afaErtek>{net * 0.27}</afaErtek>
                                <bruttoErtek>{net* 1.27}</bruttoErtek>
                            </tetel>"""
            return ret_str

        data = {
            "city_field": "Telepules2",
            "update_data": update_data_garancia,
            "zip_field": "Iranyitoszam2",
            "address_field": "Cim3",
            "calc_net_price": calc_net_price,
            "proform_number_field": "DijbekeroSzama3",
            "type_name": "garancia",
            "test": False,
            "prefix": "ASZ",
        }
        client.create_invoice_or_proform(
            criteria=garancia_proform_criteria,
            proform=True,
            cash=False,
            messages_field="DijbekeroUzenetek2",
            note_field="DijbekeroMegjegyzes3",
            items=garancia_items,
            **data,
        )
