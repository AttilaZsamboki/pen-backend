import os
import requests
from dotenv import load_dotenv
load_dotenv()


def get_request(endpoint, id=None, query_params=None):
    system_id = os.environ.get("PEN_MINICRM_SYSTEM_ID")
    api_key = os.environ.get("PEN_MINICRM_API_KEY")

    data = requests.get(
        f"https://r3.minicrm.hu/Api/R3/{endpoint}{'/'+str(id) if id else ''}", auth=(system_id, api_key), params=query_params)
    return data.json()


def update_adatlap_fields(id, fields):
    system_id = os.environ.get("PEN_MINICRM_SYSTEM_ID")
    api_key = os.environ.get("PEN_MINICRM_API_KEY")

    adatlap = requests.put(
        f'https://r3.minicrm.hu/Api/R3/Project/{id}', auth=(system_id, api_key), json=fields)
    if adatlap.status_code == 200:
        return {"code": 200, "data": adatlap.json()}
    else:
        return {"code": adatlap.status_code, "reason": adatlap.reason}


def get_all_adatlap(category_id, status_id=None):
    query_params = {"CategoryId": category_id} if not status_id else {
        "CategoryId": category_id, "StatusId": status_id}
    return get_request(endpoint="Project", query_params=query_params)


def adatlap_details(id):
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