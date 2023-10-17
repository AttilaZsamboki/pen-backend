import os
import requests
import random
import json


from dotenv import load_dotenv

load_dotenv()


def get_request(endpoint, id=None, query_params=None, isR3=True):
    system_id = os.environ.get("PEN_MINICRM_SYSTEM_ID")
    api_key = os.environ.get("PEN_MINICRM_API_KEY")

    data = requests.get(
        f"https://r3.minicrm.hu/Api/{'R3/' if isR3 else ''}{endpoint}{'/'+str(id) if id else ''}",
        auth=(system_id, api_key),
        params=query_params,
    )
    if data.status_code == 200:
        return {"status": "Success", "response": data.json()}
    else:
        return {"status": "Error", "response": data.text}


def update_request(id, fields={}, endpoint="Project", isR3=True, method="PUT"):
    system_id = os.environ.get("PEN_MINICRM_SYSTEM_ID")
    api_key = os.environ.get("PEN_MINICRM_API_KEY")

    if method == "PUT":
        return requests.put(
            f'https://r3.minicrm.hu/Api{"/R3" if isR3 else ""}/{endpoint}/{id}',
            auth=(system_id, api_key),
            json=fields,
        )
    elif method == "POST":
        return requests.post(
            f'https://r3.minicrm.hu/Api{"/R3" if isR3 else ""}/{endpoint}/{id}',
            auth=(system_id, api_key),
            json=fields,
        )


def update_adatlap_fields(id, fields):
    adatlap = update_request(id=id, fields=fields, endpoint="Project")
    if adatlap.status_code == 200:
        return {"code": 200, "data": adatlap.json()}
    else:
        return {"code": adatlap.status_code, "reason": adatlap.reason}


def get_all_adatlap(category_id, status_id=None, criteria=None, deleted=False):
    query_params = (
        {"CategoryId": category_id}
        if not status_id
        else {"CategoryId": category_id, "StatusId": status_id}
    )
    adatlapok = get_request(endpoint="Project", query_params=query_params)
    if adatlapok["status"] == "Error":
        return "Error"
    if deleted:
        adatlapok = [
            adatlap
            for adatlap in adatlapok["response"]["Results"]
            if adatlap[deleted] == 0
        ]
    if criteria:
        return [
            adatlap
            for adatlap in adatlapok["response"]["Results"].values()
            if criteria(adatlap)
        ]
    return adatlapok["response"]


def get_adatlap_details(id):
    return get_request(endpoint="Project", id=id)


def contact_details(contact_id=None, adatlap_id=None):
    if adatlap_id and not contact_id:
        contact_id = get_adatlap_details(adatlap_id)["response"]["ContactId"]
    return get_request("Contact", id=contact_id)


def get_all_contacts(adatlap_ids, type="ContactId"):
    contacts = []
    for adatlap_id in adatlap_ids:
        adatlap_details = get_adatlap_details(adatlap_id)
        if adatlap_details["status"] == "Error":
            return "Error"
        contacts.append(
            {
                "AdatlapId": adatlap_id,
                **contact_details(adatlap_details["response"][type])["response"],
            }
        )
    return contacts


def address_ids(contact_id):
    return get_request("AddressList", id=contact_id)["response"]["Results"].keys()


def address_details(address_id):
    return get_request("Address", id=address_id)


def get_all_addresses(contact_ids):
    addresses = []
    for contact_id in contact_ids:
        addresses.append(address_list(contact_id=contact_id))
    return addresses


def address_list(contact_id):
    return [address_details(i)["response"] for i in address_ids(contact_id)]


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
        f"https://r3.minicrm.hu/Api/R3/ToDo/", auth=(system_id, api_key), params=data
    )


def get_all_adatlap_details(
    category_id=None, status_id=None, criteria=None, deleted=False, ids=None
):
    if not ids:
        adatlapok = get_all_adatlap(
            category_id=category_id, status_id=status_id, deleted=deleted
        )
        if adatlapok == "Error":
            return "Error"
        adatlapok_detailed = []
        for i in adatlapok["Results"]:
            adatlap = get_adatlap_details(adatlapok["Results"][i]["Id"])["response"]
            if criteria:
                if criteria(adatlap):
                    adatlapok_detailed.append(adatlap)
                continue
            adatlapok_detailed.append(adatlap)
        return adatlapok_detailed
    else:
        adatlapok_detailed = []
        for id in ids:
            adatlap = get_adatlap_details(id)["response"]
            if criteria:
                if criteria(adatlap):
                    adatlapok_detailed.append(adatlap)
                continue
            adatlapok_detailed.append(adatlap)
        return adatlapok_detailed


def list_to_dos(adatlap_id, criteria=None):
    todos = get_request(endpoint="ToDoList", id=adatlap_id)
    if todos["status"] == "Error":
        return
    if criteria:
        return [todo for todo in todos["response"]["Results"] if criteria(todo)]
    return todos


def update_all_status(status, condition, category_id):
    adatlapok = get_all_adatlap_details(category_id=category_id)
    updated_adatlapok = []
    for adatlap in adatlapok:
        if condition(adatlap):
            updated_adatlapok.append(
                update_adatlap_fields(id=adatlap["Id"], fields={"StatusId": status})
            )
    return updated_adatlapok


statuses = {
    "Felmérés": {
        "Elszámolásra vár": 3084,
        "Sikeres felmérés": 3086,
    },
    "ToDo": {"Felmérés": 225},
}


def update_todo(id, fields):
    update_request(id=id, fields=fields, endpoint="ToDo")


def create_order(
    adatlap_id, contact_id, offer_id, adatlap_status=None, project_data=None
):
    adatlap = get_adatlap_details(id=adatlap_id)["response"]
    contactData = contact_details(contact_id=contact_id)["response"]
    offerData = get_offer(offer_id)["response"]
    if offerData == "Error":
        return {"status": "error", "response": "Offer not found"}
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

    system_id = os.environ.get("PEN_MINICRM_SYSTEM_ID")
    api_key = os.environ.get("PEN_MINICRM_API_KEY")

    data = requests.post(
        f"https://r3.minicrm.hu/Api/SyncFeed/119/Upload",
        auth=(system_id, api_key),
        data=xml_string.encode("utf-8"),
        headers={"Content-Type": "application/xml"},
    )
    if data.status_code == 200:
        return {"status": "success", "response": data.json()}
    else:
        return {"status": "error", "response": data.text, "xml": xml_string}


def get_offer(offer_id):
    return get_request(endpoint="Offer", id=offer_id, isR3=False)


def get_order(order_id):
    return get_request(endpoint="Order", id=order_id, isR3=False)


def update_offer_order(offer_id, fields, project=True, type="Offer"):
    return update_request(
        id=str(offer_id) + ("/Project" if project else ""),
        fields=fields,
        endpoint=type,
        isR3=False,
        method="POST",
    )


def get_order_address(order_id):
    address = get_order(order_id=order_id)
    return {
        "status": address["status"],
        "response": address["response"]["Customer"]
        if address["status"] == "Success"
        else address["response"],
    }


def update_order_status(order_id, status="Complete"):
    return update_request(
        id=str(order_id) + "/" + status, method="POST", isR3=False, endpoint="Order"
    )
