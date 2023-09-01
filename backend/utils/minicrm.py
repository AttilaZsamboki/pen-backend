import os
import requests
import random
from dotenv import load_dotenv
load_dotenv()


def get_request(endpoint, id=None, query_params=None, isR3=True):
    system_id = os.environ.get("PEN_MINICRM_SYSTEM_ID")
    api_key = os.environ.get("PEN_MINICRM_API_KEY")

    data = requests.get(
        f"https://r3.minicrm.hu/Api/{'R3/' if isR3 else ''}{endpoint}{'/'+str(id) if id else ''}", auth=(system_id, api_key), params=query_params)
    if data.status_code == 200:
        return data.json()
    else:
        return "Error"

def update_request(id, fields, endpoint):
    system_id = os.environ.get("PEN_MINICRM_SYSTEM_ID")
    api_key = os.environ.get("PEN_MINICRM_API_KEY")

    return requests.put(
        f'https://r3.minicrm.hu/Api/R3/{endpoint}/{id}', auth=(system_id, api_key), json=fields)

def update_adatlap_fields(id, fields):
    adatlap = update_request(id=id, fields=fields, endpoint="Project")
    if adatlap.status_code == 200:
        return {"code": 200, "data": adatlap.json()}
    else:
        return {"code": adatlap.status_code, "reason": adatlap.reason}


def get_all_adatlap(category_id, status_id=None):
    query_params = {"CategoryId": category_id} if not status_id else {
        "CategoryId": category_id, "StatusId": status_id}
    return get_request(endpoint="Project", query_params=query_params)


def get_adatlap_details(id):
    return get_request(
        endpoint="Project", id=id)


def contact_details(contact_id):
    return get_request(
        "Contact", id=contact_id)


def address_ids(contact_id):
    return get_request("AddressList", id=contact_id)["Results"].keys()


def address_details(address_id):
    return get_request(
        "Address", id=address_id)


def address_list(contact_id):
    return [address_details(
        i) for i in address_ids(contact_id)]


def billing_address(contact_id):
    addresses = address_list(contact_id=contact_id)
    for address in addresses:
        if address["Type"] == "Számlázási cím":
            return address

def create_to_do(adatlap_id, user, type, comment, deadline):
    system_id = os.environ.get("PEN_MINICRM_SYSTEM_ID")
    api_key = os.environ.get("PEN_MINICRM_API_KEY")
    data = {
        "ProjectId": adatlap_id,
        "UserId": user,
        "Type": type,
        "Comment": comment,
        "Deadline": deadline,
    }

    return requests.put(
        f"https://r3.minicrm.hu/Api/R3/ToDo/", auth=(system_id, api_key), params=data)

def get_all_adatlap_details(category_id, status_id=None, criteria=None, deleted=False):
    adatlapok = get_all_adatlap(category_id=category_id, status_id=status_id)
    if adatlapok == "Error":
        return "Error"
    adatlapok_detailed = []
    for i in adatlapok["Results"]:
        if adatlapok["Results"][i]["Deleted"] != deleted:
            continue
        adatlap = get_adatlap_details(adatlapok["Results"][i]["Id"])
        if criteria:
            if criteria(adatlap):
                adatlapok_detailed.append(adatlap)
            continue
        adatlapok_detailed.append(adatlap)
    return adatlapok_detailed

def list_to_dos(adatlap_id, criteria=None):
    todos = get_request(endpoint="ToDoList", id=adatlap_id)
    if todos == "Error":
        return 
    if criteria:
        return [todo for todo in todos["Results"] if criteria(todo)]
    return todos


def update_all_status(status, condition, category_id):
    adatlapok = get_all_adatlap_details(category_id=category_id)
    updated_adatlapok = []
    for adatlap in adatlapok:
        if condition(adatlap):
            updated_adatlapok.append(update_adatlap_fields(id=adatlap["Id"], fields={"StatusId": status}))
    return updated_adatlapok

statuses = {
    "Felmérés": {
        "Elszámolásra vár": 3084,
        "Sikeres felmérés": 3086,
    },
    "ToDo": {
        "Felmérés": 225
    }
}

def update_todo(id, fields):
    update_request(id=id, fields=fields, endpoint="ToDo")

def create_order(adatlap_id, contact_id, items, offer_id, adatlap_status=None):
    adatlap = get_adatlap_details(id=adatlap_id)
    contactData = contact_details(contact_id=contact_id)
    offerData = get_offer(offer_id)
    if offerData == "Error":
        return "Error"
    randomId = random.randint(100000, 999999)
    products = '\n'.join([
        f'''<Product Id="{item['productId']}">
        <!-- Name of product [required int] -->
        <Name>{item['name']}</Name>
        <!-- SKU code of product [optional string]-->
        <SKU>{item['sku']}</SKU>
        <!-- Nett price of product [required int] -->
        <PriceNet>{item['netPrice']}</PriceNet>
        <!-- Quantity of product [required int] -->
        <Quantity>{sum(value['ammount'] for value in item['inputValues'])}</Quantity>
        <!-- Unit of product [required string] -->
        <Unit>darab</Unit>
        <!-- VAT of product [required int] -->
        <VAT>27%</VAT>
        <!-- Folder of product in MiniCRM. If it does not exist, then it is created automaticly [required string] -->
        <FolderName>Default products</FolderName>
    </Product>''' for item in items
    ])
    xml_string = f"""<?xml version="1.0" encoding="UTF-8"?>
<Projects>
    <Project Id="{randomId}">
        <StatusId>3099</StatusId>
        <Name>{adatlap["Name"]}</Name>
        <ContactId>{contact_id}</ContactId>
        <UserId>{adatlap["UserId"]}</UserId>
        <CategoryId>32</CategoryId>
        <Contacts>
            <Contact Id="{randomId}">
                <FirstName>{contactData["FirstName"]}</FirstName>
                <LastName>{contactData["LastName"]}</LastName>
                <Type>{contactData["Type"]}</Type>
                <Email>{contactData["Email"]}</Email>
                <Phone>{contactData["Phone"]}</Phone>
            </Contact>
        </Contacts>
        <Orders>
            <Order Id="{randomId}">
                <Number>{adatlap["Name"]}</Number>
                <CurrencyCode>HUF</CurrencyCode>
                <!-- Performace date of order [required date] -->
                <Performance>2015-09-22 12:15:13</Performance>
                <Status>Draft</Status>
                <!-- Data of Customer -->
                <Customer>
                    <!-- Name of Customer [required string] -->
                    <Name>{contactData["LastName"]} {contactData["FirstName"]}</Name>
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
                </Project>
            </Order>
        </Orders>
    </Project>
</Projects>"""

    system_id = os.environ.get("PEN_MINICRM_SYSTEM_ID")
    api_key = os.environ.get("PEN_MINICRM_API_KEY")

    data = requests.post(
        f"https://r3.minicrm.hu/Api/SyncFeed/119/Upload", auth=(system_id, api_key), data=xml_string.encode("utf-8"))
    if data.status_code == 200:
        return data.json()
    else:
        return "Error"

def get_offer(offer_id):
    return get_request(endpoint="Offer", id=offer_id, isR3=False)