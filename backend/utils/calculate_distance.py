import codecs
from .minicrm import update_adatlap_fields, get_adatlap_by_id
from ..utils.google_maps import get_street_view

data = get_adatlap_by_id("41587")["data"]
address = f"{data['Cim2']} {data['Telepules']}, {data['Iranyitoszam']} {data['Orszag']}"
print(address)
print(get_street_view(location=address))
print(update_adatlap_fields("41587", {
    "IngatlanKepe": "https://www.dataupload.xyz/static/images/google_street_view/street_view.jpg"}))
