import json
import requests
import os
import dotenv
dotenv.load_dotenv()

API_KEY = os.environ.get("PEN_MINICRM_API_KEY")
SYSTEM_ID = os.environ.get("PEN_MINICRM_SYSTEM_ID")

# costumers = [
#     # {"contact_name": "Tesztelő János", "name": "ML2023-E/00010 (E-munkalap)"},
#     {"contact_name": "Teszt Mackó", "name": "ML2023-E/00011 (E-munkalap)"},
# ]

# for i in costumers:
#     contact = requests.get(
#         'https://r3.minicrm.hu/Api/R3/Contact', params={"Name": i["contact_name"]}, auth=(SYSTEM_ID, API_KEY)).json()
#     print(json.dumps(contact, indent=4))
#     contact_id = list(contact["Results"].keys())[0]
#     data = requests.get(
#         'https://r3.minicrm.hu/Api/R3/Project', params={"MainContactId": contact_id, "CategoryId": 28, "Name": i["name"]}, auth=(SYSTEM_ID, API_KEY)
#     )
#     user_id = list(data.json()["Results"].keys())[0]
#     print(user_id)

update = requests.put(
    'https://r3.minicrm.hu/Api/R3/Project/41470', auth=(SYSTEM_ID, API_KEY), json={"MegjegyzesLeiras": "Helyi elszívós rendszer"})
print(update.text)
