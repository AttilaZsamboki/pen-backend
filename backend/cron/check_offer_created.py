from ..utils.logs import log
import datetime
import os
import random
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

import dotenv
import requests
from django.db.models import Q

from ..models import Felmeresek, FelmeresItems, MiniCrmAdatlapok
from ..utils.minicrm import contact_details
from ..utils.minicrm_str_to_text import status_map

dotenv.load_dotenv()

felmeresek = Felmeresek.objects.filter(
    ~Q(
        id__in=list(
            MiniCrmAdatlapok.objects.values_list("Felmeresid", flat=True)
            .filter(Felmeresid__isnull=False, Deleted=1)
            .exclude(Felmeresid="None")
        )
    ),
    status__in=["COMPLETED", "IN_PROGRESS"],
)


def prettify(elem):
    rough_string = tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def assemble_offer_xml(
    adatlap,
    items,
    felmeres,
    user_id=39636,
    template_name=None,
):
    random_id = random.randint(0, 1000000)
    contact_data = contact_details(adatlap.ContactId)
    if contact_data["status"] == "Error":
        return
    contact_data = contact_data["response"]
    date = datetime.datetime.now() + datetime.timedelta(days=30)

    projects = Element("Projects")
    project = SubElement(projects, "Project")
    project.set("Id", str(random_id))
    SubElement(project, "StatusId").text = "3099"
    SubElement(project, "Name").text = adatlap.Name
    SubElement(project, "ContactId").text = str(contact_data["Id"])
    SubElement(project, "UserId").text = str(user_id)
    SubElement(project, "CategoryId").text = "32"

    contacts = SubElement(project, "Contacts")
    contact = SubElement(contacts, "Contact")
    contact.set("Id", str(random_id))
    SubElement(contact, "FirstName").text = contact_data["FirstName"]
    SubElement(contact, "LastName").text = contact_data["LastName"]
    SubElement(contact, "Type").text = contact_data["Type"]
    SubElement(contact, "Email").text = contact_data["Email"]
    SubElement(contact, "Phone").text = contact_data["Phone"]

    offers = SubElement(project, "Offers")
    offer = SubElement(offers, "Offer")
    offer.set("Id", str(random_id))
    SubElement(offer, "Number").text = (
        adatlap.Name + " - " + (template_name[:20] if template_name else "Egyéni")
    )
    SubElement(offer, "CurrencyCode").text = "HUF"
    SubElement(offer, "Subject").text = felmeres.subject
    SubElement(offer, "Performance").text = date.strftime("%Y-%m-%d")
    SubElement(offer, "Prompt").text = date.strftime("%Y-%m-%d")
    SubElement(offer, "Status").text = "2895"

    customer = SubElement(offer, "Customer")
    SubElement(customer, "Name").text = (
        contact_data["LastName"] + " " + contact_data["FirstName"]
    )
    SubElement(customer, "CountryId").text = adatlap.Orszag
    SubElement(customer, "PostalCode").text = adatlap.Iranyitoszam
    SubElement(customer, "City").text = adatlap.Telepules
    SubElement(customer, "Address").text = adatlap.Cim2

    products = SubElement(offer, "Products")
    for item in items:
        product = SubElement(products, "Product")
        product.set(
            "Id",
            str(item.product_id if item.product_id else random.randint(0, 1000)),
        )
        SubElement(product, "Name").text = item.name
        SubElement(product, "SKU").text = (
            item.product.sku if item.product else str(random.randint(0, 1000))
        )
        SubElement(product, "PriceNet").text = str(item.netPrice)
        SubElement(product, "Quantity").text = str(
            sum([i["ammount"] for i in item.inputValues])
        )
        SubElement(product, "Unit").text = "darab"
        SubElement(product, "VAT").text = "27%"
        SubElement(product, "FolderName").text = "Default products"

    project_element = SubElement(offer, "Project")
    SubElement(project_element, "Felmeresid").text = str(felmeres.id)
    SubElement(project_element, "UserId").text = (
        str(adatlap.Felmero2) if adatlap.Felmero2 else ""
    )
    SubElement(
        project_element, "KapcsolodoFelmeres"
    ).text = "https://app.peneszmentesites.hu/" + str(felmeres.id)
    SubElement(project_element, "ArajanlatMegjegyzes").text = felmeres.description

    xml_string = prettify(projects)

    system_id = os.environ.get("PEN_MINICRM_SYSTEM_ID")
    api_key = os.environ.get("PEN_MINICRM_API_KEY")

    return requests.post(
        f"https://r3.minicrm.hu/Api/SyncFeed/119/Upload",
        auth=(system_id, api_key),
        data=xml_string.encode("utf-8"),
        headers={"Content-Type": "application/xml"},
    )


def main():
    for felmeres in felmeresek:
        log(
            "Árajánlat generálása",
            "INFO",
            "pen_check_offer_created",
            "Felmérés: " + str(felmeres.id) + " - " + str(felmeres.adatlap_id),
        )
        assemble_offer_xml(
            adatlap=felmeres.adatlap_id,
            items=FelmeresItems.objects.filter(adatlap_id=felmeres.id),
            felmeres=felmeres,
            template_name=felmeres.template.name if felmeres.template else None,
        )
        return


main()
