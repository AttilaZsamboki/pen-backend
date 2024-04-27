import os
import random
import sys
from dataclasses import dataclass, field
from typing import List
import django

import requests
from dotenv import load_dotenv
from requests.models import Response


sys.path.append(os.path.abspath("/home/atti/googleds/dataupload"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "peneszmentesites.settings")
if not "DJANGO_SETTINGS_MODULE" in os.environ:
    django.setup()

load_dotenv()


@dataclass
class Todo:
    Id: int
    Status: str
    Comment: str
    Deadline: str
    UserId: int
    Type: int
    Url: str


@dataclass
class Adatlap:
    Id: int
    Name: str
    Url: str
    ContactId: int
    StatusId: int
    UserId: int
    Deleted: int


@dataclass()
class Contact:
    Id: int = field(default=None)
    Type: str = field(default=None)
    Name: str = field(default=None)
    FirstName: str = field(default=None)
    LastName: str = field(default=None)
    Email: str = field(default=None)
    Phone: str = field(default=None)
    Description: str = field(default=None)
    Deleted: int = field(default=None)
    CreatedBy: str = field(default=None)
    CreatedAt: str = field(default=None)
    UpdatedBy: str = field(default=None)
    UpdatedAt: str = field(default=None)
    Url: str = field(default=None)
    BankAccount: str = field(default=None)
    Swift: str = field(default=None)
    RegistrationNumber: str = field(default=None)
    VatNumber: str = field(default=None)
    Industry: str = field(default=None)
    Region: str = field(default=None)
    Employees: int = field(default=None)
    YearlyRevenue: int = field(default=None)
    EUVatNumber: str = field(default=None)
    FoundingYear: int = field(default=None)
    Capital: int = field(default=None)
    MainActivity: str = field(default=None)
    BisnodeTrafficLight: str = field(default=None)
    GroupIdentificationNumber: str = field(default=None)
    NonGovernmentalOrganization: str = field(default=None)
    MegjegyzesACimmelKapcsolatban: str = field(default=None)
    Tags: List[str] = field(default=None)
    Position: str = field(default=None)
    DataManagement_Consent: str = field(default=None)
    MegjegyzesACimmelKapcsolatban2: str = field(default=None)
    SzamlazasiNev: str = field(default=None)
    BusinessId: int = field(default=None)

    @property
    def FullName(self):
        if self.Name:
            return self.Name
        return self.LastName + " " + self.FirstName


@dataclass
class AdatlapDetails:
    Id: str
    CategoryId: str
    ContactId: str
    StatusId: str
    UserId: str
    Name: str
    StatusUpdatedAt: str
    IsPrivate: str
    Invited: str
    Deleted: str
    CreatedBy: str
    CreatedAt: str
    UpdatedBy: str
    UpdatedAt: str
    EmailOpen_Phone: str
    EmailOpen_Tablet: str
    EmailOpen_iPhone: str
    EmailOpen_iPad: str
    EmailOpen_Android: str
    Serial_Number: str
    Type: str
    Url: str
    MilyenProblemavalFordultHozzank: str
    Tavolsag: str
    FelmeresiDij: str
    FelmeresIdopontja2: str
    MiAzUgyfelFoSzempontja3: str
    EgyebSzempontok3: str
    Cim2: str
    UtazasiIdoKozponttol: str
    Alaprajz: str
    LezarasOka: str
    LezarasSzovegesen: str
    Telepules: str
    Iranyitoszam: str
    Forras: str
    Megye: str
    Orszag: str
    Felmero2: str
    DijbekeroPdf2: str
    DijbekeroSzama2: str
    DijbekeroMegjegyzes2: str
    DijbekeroUzenetek: str
    FizetesiMod2: str
    KiallitasDatuma: str
    FizetesiHatarido: str
    MennyireVoltMegelegedve2: str
    Pontszam3: str
    SzovegesErtekeles4: str
    IngatlanKepe: str
    Munkalap: str
    BruttoFelmeresiDij: str
    MunkalapMegjegyzes: str
    FelmeresVisszaigazolva: str
    SzamlaPdf: str
    SzamlaSorszama2: str
    KiallitasDatuma2: str
    SzamlaUzenetek: str
    SzamlaMegjegyzes: str
    FelmeresAdatok: str
    UtvonalAKozponttol: str
    StreetViewUrl: str
    TervezettFelmresIdopont: str
    MiertMentunkKiFeleslegesen: str
    NemElerheto: str
    BefizetesMegerkezett: str
    VisszafizetesDatuma: str
    HelyesbitoSzamla: str
    HelysesbitoSzamlaSzama: str
    Kapcsolat: str
    SzamlazasIngatlanCimre2: str
    GaranciaszerzodesMinta: str
    SzerzodesMintatKert: str
    IngatlanHasznalata2: str
    BusinessId: str
    ProjectHash: str
    ProjectEmail: str


@dataclass
class Address:
    Id: int
    ContactId: int
    Type: str
    Name: str
    CountryId: str
    PostalCode: str
    City: str
    County: str
    Address: str
    Default: int
    CreatedBy: str
    CreatedAt: str
    UpdatedBy: str
    UpdatedAt: str


@dataclass
class TodoDetails:
    Id: int
    UserId: str
    ContactId: int
    ProjectId: int
    Type: str
    Duration: int
    Reminder: int
    Status: str
    Mode: str
    Deadline: str
    Comment: str
    CreatedBy: str
    CreatedAt: str
    UpdatedBy: str
    UpdatedAt: str
    ClosedBy: str
    ClosedAt: str
    AddressId: int
    SenderUserId: int
    Attachments: List[str]
    Members: List[str]
    Notes: List[str]


@dataclass
class MiniCrmResponse:
    Count: int
    Results: List[dict]


class MiniCrmClient:
    base_url = "https://r3.minicrm.hu/Api/"

    def __init__(
        self,
        system_id=os.environ.get("PEN_MINICRM_SYSTEM_ID"),
        api_key=os.environ.get("PEN_MINICRM_API_KEY"),
        description=None,
        script_name=None,
    ):
        self.script_name = script_name
        self.description = description
        self.system_id = system_id
        self.api_key = api_key

    def list_todos(self, adatlap_id, criteria=lambda _: True) -> List[Todo]:
        todos = self.get_request(endpoint="ToDoList", id=adatlap_id)
        return [Todo(**todo) for todo in todos.Results if criteria(todo)]

    def get_request(
        self,
        endpoint,
        id=None,
        query_params=None,
        isR3=True,
    ) -> Response:
        from ..utils.logs import log_minicrm_request

        endpoint = f"{'R3/' if isR3 else ''}{endpoint}{'/'+str(id) if id else ''}"
        log_minicrm_request(
            endpoint=endpoint,
            script=self.script_name,
            description=self.description,
        )
        return requests.get(
            f"{self.base_url}{endpoint}",
            auth=(self.system_id, self.api_key),
            params=query_params,
        )

    def get_adatlap(
        self, category_id, status_id=None, criteria=lambda _: True, deleted=False
    ):
        query_params = {"CategoryId": category_id}
        if status_id:
            query_params["StatusId"] = status_id

        adatlapok = self.get_request(endpoint="Project", query_params=query_params)

        return [
            Adatlap(**adatlap)
            for adatlap in adatlapok.json()
            if criteria(adatlap) and (adatlap["Deleted"] == 0 or deleted)
        ]

    def get_adatlap_details(
        self,
        id,
    ):
        return AdatlapDetails(
            **self.get_request(
                endpoint="Project",
                id=id,
            ).Results
        )

    def contact_details(self, contact_id=None, adatlap_id=None):
        if adatlap_id and not contact_id:
            contact_id = self.get_adatlap_details(adatlap_id).ContactId
        resp = self.get_request(
            "Contact",
            id=contact_id,
        )

        if resp.ok:
            return Contact(**resp.json())
        else:
            return Contact()

    def address_ids(
        self,
        contact_id,
    ) -> List[int]:
        resp = self.get_request(
            "AddressList",
            id=contact_id,
        )
        return resp.Results.keys()

    def address_details(self, address_id: int):
        return Address(
            **self.get_request(
                "Address",
                id=address_id,
            )
        )

    def address_list(self, contact_id):
        return [self.address_details(i) for i in self.address_ids(contact_id)]

    def get_address(self, contact_id, typeof="Számlázási cím"):
        addresses = self.address_list(contact_id=contact_id)
        for address in addresses:
            if address.Type == typeof:
                return address
        return None

    def todo_details(self, todo_id):
        return TodoDetails(
            **self.get_request(
                endpoint="ToDo",
                id=todo_id,
            )
        )

    def get_order(self, order_id):
        return self.get_request(endpoint="Order", id=order_id, isR3=False)

    def create_order(
        self,
        adatlap,
        offer_id,
        adatlap_status=None,
        project_data=None,
    ):
        contactData = self.contact_details(contact_id=adatlap.ContactId)
        offerData = self.get_offer(offer_id).Results
        randomId = random.randint(100000, 999999)
        products = "\n".join(
            [
                f"""<Product Id="{item['Id']}">
            <!-- Name of product [required int] -->
            <Name>{item['Name']}</Name>
            <!-- SKU code of product [optional string]-->
            <SKU>{item['SKU']}</SKU>
            <!-- Nett price of product [required int] -->
            <PriceNet>{item['PriceNet']}</PriceNet>
            <!-- Quantity of product [required int] -->
            <Quantity>{item["Quantity"]}</Quantity>
            <!-- Unit of product [required string] -->
            <Unit>darab</Unit>
            <!-- VAT of product [required int] -->
            <VAT>27%</VAT>
            <!-- Folder of product in MiniCRM. If it does not exist, then it is created automaticly [required string] -->
            <FolderName>Default products</FolderName>
        </Product>"""
                for item in offerData["Items"]
            ]
        )
        xml_string = (
            f"""<?xml version="1.0" encoding="UTF-8"?>
    <Projects>
        <Project Id="{randomId}">
            <StatusId>3099</StatusId>
            <Name>{adatlap.Name}</Name>
            <ContactId>{adatlap.ContactId}</ContactId>
            <UserId>{adatlap.UserId}</UserId>
            <CategoryId>32</CategoryId>
            <Contacts>
                <Contact Id="{randomId}">
                    <FirstName>{contactData.FirstName}</FirstName>
                    <LastName>{contactData.LastName}</LastName>
                    <Type>{contactData.Type}</Type>
                    <Email>{contactData.Email}</Email>
                    <Phone>{contactData.Phone}</Phone>
                </Contact>
            </Contacts>
            <Orders>
                <Order Id="{randomId}">
                    <Number>{adatlap.Name}</Number>
                    <CurrencyCode>HUF</CurrencyCode>
                    <!-- Performace date of order [required date] -->
                    <Performance>2015-09-22 12:15:13</Performance>
                    <Status>Draft</Status>
                    <!-- Data of Customer -->
                    <Customer>
                        <!-- Name of Customer [required string] -->
                        <Name>{contactData.LastName} {contactData.FirstName}</Name>
                        <!-- Country of customer [required string] -->
                        <CountryId>Magyarország</CountryId>
                        <!-- Postalcode of customer [required string] -->
                        <PostalCode>{offerData["Customer"]["PostalCode"]}</PostalCode>
                        <!-- City of customer [required string] -->
                        <City>{offerData["Customer"]["City"]}</City>
                        <!-- Address of customer [required string] -->
                        <Address>{offerData["Customer"]["Address"]}</Address>
                    </Customer>
                    <!-- Data of product -->
                    <Products>
                        <!-- Id = External id of product [required int] -->
                        {products}
                    </Products>
                    <Project>
                        <Enum1951>{adatlap_status if adatlap_status else ''}</Enum1951>
                        """
            + "\n".join(
                [f"<{k}><![CDATA[{v}]]></{k}>" for k, v in project_data.items() if v]
            )
            + """
                    </Project>
                </Order>
            </Orders>
        </Project>
    </Projects>"""
        )

        return requests.post(
            f"https://r3.minicrm.hu/Api/SyncFeed/119/Upload",
            auth=(self.system_id, self.api_key),
            data=xml_string.encode("utf-8"),
            headers={"Content-Type": "application/xml"},
        )

    def get_offer(self, offer_id):
        return self.get_request(endpoint="Offer", id=offer_id, isR3=False)

    def update_request(
        self, id, fields={}, endpoint="Project", isR3=True, method="PUT"
    ):
        from ..utils.logs import log_minicrm_request

        endpoint = f'{"/R3" if isR3 else ""}/{endpoint}/{id}'
        if method == "PUT":
            log_minicrm_request(endpoint=endpoint, script=self.script_name)
            return requests.put(
                f"https://r3.minicrm.hu/Api{endpoint}",
                auth=(self.system_id, self.api_key),
                json=fields,
            )
        elif method == "POST":
            log_minicrm_request(endpoint=endpoint, script=self.script_name)
            return requests.post(
                f"https://r3.minicrm.hu/Api{endpoint}",
                auth=(self.system_id, self.api_key),
                json=fields,
            )

    def update_adatlap_fields(self, id, fields):
        return self.update_request(id=id, fields=fields, endpoint="Project")

    def create_to_do(self, adatlap_id, user, type, comment, deadline):
        from ..utils.logs import log_minicrm_request

        data = {
            "ProjectId": adatlap_id,
            "UserId": user,
            "Type": type,
            "Comment": comment,
            "Deadline": deadline,
        }

        log_minicrm_request(
            endpoint="ToDo",
            script=self.script_name,
            description="MiniCRM ToDo létrehozása",
        )
        return requests.put(
            f"https://r3.minicrm.hu/Api/R3/ToDo/",
            auth=(self.system_id, self.api_key),
            params=data,
        )

    def update_todo(self, id, fields):
        return self.update_request(id=id, fields=fields, endpoint="ToDo")

    def update_offer_order(self, offer_id, fields, project=True, type="Offer"):
        return self.update_request(
            id=str(offer_id) + ("/Project" if project else ""),
            fields=fields,
            endpoint=type,
            isR3=False,
            method="POST",
        )

    def update_order_status(self, order_id, status="Complete"):
        return self.update_request(
            id=str(order_id) + "/" + status, method="POST", isR3=False, endpoint="Order"
        )
