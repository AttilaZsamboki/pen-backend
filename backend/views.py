import datetime
import json
import os
import random
import re
import string
import traceback
import uuid
import xml.etree.ElementTree as ET

# Create your views here.
from typing import Dict, List

import boto3
from django.db import connection
from django.db.models import CharField, F, Q, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
)
from rest_framework.views import APIView
from rest_framework_xml.parsers import XMLParser
from rest_framework_xml.renderers import XMLRenderer

from . import models, serializers
from .auth0backend import CustomJWTAuthentication
from .scripts.api_scripts import mini_crm_proxy
from .utils.calculate_distance import calculate_distance_fn
from .utils.logs import log
from .utils.minicrm import (
    address_details,
    address_ids,
    contact_details,
    update_offer_order,
)
from .utils.utils import get_address, replace_self_closing_tags


def map_wh_fields(data: Dict, field_names: List[str]):
    def map_wh_field(data, field_name):
        return (
            data["Schema"][field_name][str(data["Data"][field_name])]
            if data["Data"][field_name]
            else None
        )

    [
        data["Data"].update({field_name: map_wh_field(data, field_name)})
        for field_name in field_names
    ]
    return data


def save_webhook(adatlap, process_data=None, name="felmeres"):
    if process_data:
        adatlap = process_data(adatlap)
    adatlap_db = models.MiniCrmAdatlapok.objects.filter(Id=adatlap["Id"])
    if adatlap_db.exists():
        adatlap_db = adatlap_db.first()
        if adatlap_db.StatusId != adatlap["StatusId"]:
            adatlap["StatusUpdatedAt"] = datetime.datetime.now()
        else:
            adatlap["StatusUpdatedAt"] = adatlap_db.StatusUpdatedAt
    else:
        adatlap["StatusUpdatedAt"] = datetime.datetime.now()

    valid_fields = {f.name for f in models.MiniCrmAdatlapok._meta.get_fields()}
    filtered_data = {k: v for k, v in adatlap.items() if k in valid_fields}

    models.MiniCrmAdatlapok(
        **filtered_data,
    ).save()
    return adatlap


class CalculateDistance(APIView):
    def post(self, request):
        data = json.loads(request.body)
        log("Felmérés webhook meghívva", "INFO", "pen_felmeres_webhook", data=data)
        data = map_wh_fields(
            data,
            ["Felmero2", "FizetesiMod2", "SzamlazasIngatlanCimre2"],
        )["Data"]

        save_webhook(data)

        if data["StatusId"] == "2927" and data["UtvonalAKozponttol"] is None:

            def update_data(duration, distance, fee, street_view_url, county, address):
                return {
                    "IngatlanKepe": "https://pen.dataupload.xyz/static/images/google_street_view/street_view.jpg",
                    "UtazasiIdoKozponttol": duration,
                    "Tavolsag": distance,
                    "FelmeresiDij": fee,
                    "StreetViewUrl": street_view_url,
                    "BruttoFelmeresiDij": round(fee * 1.27),
                    "UtvonalAKozponttol": f"https://www.google.com/maps/dir/?api=1&origin=Nagytétényi+út+218,+Budapest,+1225&destination={address}&travelmode=driving",
                    "Megye": county,
                }

            response = calculate_distance_fn(
                data,
                address=lambda x: f"{x['Cim2']} {x['Telepules']}, {x['Iranyitoszam']} {x['Orszag']}",
                update_data=update_data,
            )
            if response == "Error":
                return Response({"status": "error"}, status=HTTP_200_OK)
        return Response({"status": "success"}, status=HTTP_200_OK)

    def get(self, request):
        log(
            "Penészmentesítés webhook meghívva de 'GET' methoddal",
            "INFO",
            "pen_calculate_distance",
        )
        return Response({"status": "error"}, status=HTTP_405_METHOD_NOT_ALLOWED)


class FelmeresQuestionsList(generics.ListCreateAPIView):
    queryset = models.FelmeresQuestions.objects.all()
    serializer_class = serializers.FelmeresQuestionsSerializer
    permission_classes = [AllowAny]


class FelmeresQuestionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.FelmeresQuestions.objects.all()
    serializer_class = serializers.FelmeresQuestionsSerializer

    def get(self, request, pk):
        felmeres = models.FelmeresQuestions.objects.filter(adatlap_id=pk)
        serializer = serializers.FelmeresQuestionsSerializer(felmeres, many=True)
        return Response(serializer.data)


class OrderWebhook(APIView):
    def post(self, request):
        data = json.loads(request.body)
        log(
            "Penészmentesítés rendelés webhook meghívva",
            "INFO",
            "pen_order_webhook",
            json.dumps(data),
        )
        try:
            name_mapping = data["Schema"]["Beepitok"]

            def get_names(value):
                names = []
                keys = sorted(name_mapping.keys(), key=int, reverse=True)
                for key in keys:
                    if value >= int(key):
                        names.append(name_mapping[key])
                        value -= int(key)
                return names

            data = map_wh_fields(
                data,
                [
                    "FizetesiMod3",
                    "GaranciaTipusa",
                    "KiepitesFeltetele",
                    "KiepitesFelteteleIgazolva",
                ],
            )

            def process_data(data):
                data["Beepitok"] = ", ".join(get_names(data["Beepitok"]))
                return data

            save_webhook(data["Data"], process_data=process_data)

            models.Orders(
                adatlap_id=data["Id"],
                order_id=data["Head"]["Id"],
            ).save()
            log(
                "Penészmentesítés rendelés webhook sikeresen lefutott",
                "SUCCESS",
                "pen_order_webhook",
            )
            return Response("Succesfully received data", status=HTTP_200_OK)
        except:
            log(
                "Penészmentesítés rendelés webhook sikertelen",
                "ERROR",
                "pen_order_webhook",
                details=traceback.format_exc(),
            )
            return Response("Succesfully received data", status=HTTP_200_OK)


class ProductsList(generics.ListCreateAPIView):
    queryset = models.Products.objects.all()
    serializer_class = serializers.ProductsSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        all = request.query_params.get("all", "false")
        if all.lower() == "true":
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = models.Products.objects.all()
        filter = self.request.query_params.get("filter", None)

        if filter is not None:
            filter_words = filter.split(" ")
            q_objects = Q()

            for word in filter_words:
                q_objects &= (
                    Q(id__icontains=word)
                    | Q(name__icontains=word)
                    | Q(sku__icontains=word)
                    | Q(type__icontains=word)
                    | Q(price_list_alapertelmezett_net_price_huf__icontains=word)
                    # Add more Q objects for each column you want to search
                )

            queryset = queryset.filter(q_objects)

        query_params = self.request.query_params
        if query_params is not None:
            q_objects = Q()

            for key, value in query_params.items():
                if key != "filter" and key != "page" and key != "all":
                    q_objects &= Q(**{key + "__icontains": value})

            queryset = queryset.filter(q_objects)
            return queryset


class ProductsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Products.objects.all()
    serializer_class = serializers.ProductsSerializer
    permission_classes = [AllowAny]


class ProductAttributesList(generics.ListCreateAPIView):
    queryset = models.ProductAttributes.objects.all()
    serializer_class = serializers.ProductAttributesSerializer
    permission_classes = [AllowAny]


class ProductAttributesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ProductAttributes.objects.all()
    serializer_class = serializers.ProductAttributesSerializer
    permission_classes = [AllowAny]

    def get(self, request, pk):
        product_attributes = models.ProductAttributes.objects.filter(product_id=pk)
        serializer = serializers.ProductAttributesSerializer(
            product_attributes, many=True
        )
        return Response(serializer.data)


class FiltersList(generics.ListCreateAPIView):
    queryset = models.Filters.objects.all()
    serializer_class = serializers.FiltersSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        type_param = self.request.query_params.get("type")
        user_param = self.request.query_params.get("user")

        if type_param or user_param:
            filters = {}
            if type_param:
                filters["type"] = type_param
            if user_param:
                filters["user"] = user_param
            return models.Filters.objects.filter(**filters)
        else:
            return models.Filters.objects.all()


class FiltersDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Filters.objects.all()
    serializer_class = serializers.FiltersSerializer
    permission_classes = [AllowAny]


class QuestionsList(generics.ListCreateAPIView):
    queryset = models.Questions.objects.all()
    serializer_class = serializers.QuestionsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.query_params.get("product"):
            question_id = models.QuestionProducts.objects.filter(
                product=self.request.query_params.get("product")
            ).values("question")[0]["question"]
            return models.Questions.objects.filter(id=question_id)
        elif self.request.query_params.get("connection"):
            return models.Questions.objects.filter(
                connection=self.request.query_params.get("connection")
            )
        return super().get_queryset()


class QuestionsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Questions.objects.all()
    serializer_class = serializers.QuestionsSerializer
    permission_classes = [AllowAny]


class TemplateList(generics.ListCreateAPIView):
    queryset = models.Templates.objects.all()
    serializer_class = serializers.TemplatesSerializer
    permission_classes = [AllowAny]


class TemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Templates.objects.all()
    serializer_class = serializers.TemplatesSerializer
    permission_classes = [AllowAny]


class ProductTemplatesList(generics.ListCreateAPIView):
    queryset = models.ProductTemplate.objects.all()
    serializer_class = serializers.ProductTemplateSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        template_id = self.request.query_params.get("template_id")
        products = models.ProductTemplate.objects.filter(template=template_id)
        products.delete()
        models.ProductTemplate.objects.bulk_create(
            [
                models.ProductTemplate(
                    template=models.Templates.objects.get(id=template_id),
                    **{j: k for j, k in i.items() if j not in ["template"]},
                )
                for i in request.data
            ]
        )
        return Response(status=HTTP_200_OK)


class ProductTemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ProductTemplate.objects.all()
    serializer_class = serializers.ProductTemplateSerializer
    permission_classes = [AllowAny]

    def get(self, request, pk):
        product_templates = models.ProductTemplate.objects.filter(template=pk)
        serializer = serializers.ProductTemplateSerializer(product_templates, many=True)
        return Response(serializer.data)


from rest_framework.filters import SearchFilter


class FelmeresekList(generics.ListCreateAPIView):
    queryset = models.Felmeresek.objects.all()
    serializer_class = serializers.FelmeresekSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = [
        "adatlap_id__Name",
        "adatlap_id__Id",
        "adatlap_id__Felmero2",
        "adatlap_id__FizetesiMod2",
        "adatlap_id__Cim2",
        "adatlap_id__Telepules",
        "adatlap_id__Iranyitoszam",
        "status",
        "type",
        "subject",
        "garancia",
    ]


def felmeresek_detail(pk):
    felmeres = models.Felmeresek.objects.get(id=pk)
    adatlap = models.MiniCrmAdatlapok.objects.filter(Felmeresid=pk)
    if not adatlap.exists():
        return serializers.FelmeresekSerializer(
            {
                "adatlap_id": felmeres.adatlap_id,
                **felmeres.__dict__,
            },
        )
    adatlap = adatlap.first()
    return serializers.FelmeresekSerializer(
        {
            "offer_status": adatlap.StatusIdStr,
            "adatlap_id": felmeres.adatlap_id,
            **felmeres.__dict__,
        },
    )


class FelmeresekDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Felmeresek.objects.all()
    serializer_class = serializers.FelmeresekSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if os.environ.get("ENVIRONMENT") == "development":
            res = felmeresek_detail(pk)
            return Response(res.data)
        try:
            return Response(felmeresek_detail(pk).data)
        except Exception as e:
            log(
                "Felmérés lekérdezése sikertelen",
                "ERROR",
                "pen_felmeresek_detail",
                details=f"Error: {e}. {traceback.format_exc()}",
            )
            return Response("A felmérés nem létezik", status=HTTP_400_BAD_REQUEST)


class FelmeresItemsList(generics.ListCreateAPIView):
    queryset = models.FelmeresItems.objects.all()
    permission_classes = [AllowAny]
    serializer_class = serializers.FelmeresItemsSerializer

    def post(self, request):
        data = request.data
        adatlap_ids_in_request = [item.get("adatlap") for item in data]

        # Delete items not in request
        models.FelmeresItems.objects.filter(
            adatlap_id__in=adatlap_ids_in_request
        ).delete()

        for item in data:
            adatlap_id = item.pop("adatlap", None)
            product_id = item.pop("product", None)
            if adatlap_id is not None:
                adatlap = get_object_or_404(models.Felmeresek, id=adatlap_id)
                item["adatlap"] = adatlap
            if product_id is not None:
                product = get_object_or_404(models.Products, id=product_id)
                item["product"] = product
            item = {
                k: v
                for k, v in item.items()
                if k in [f.name for f in models.FelmeresItems._meta.get_fields()]
            }
            instance, created = models.FelmeresItems.objects.update_or_create(
                id=item.get("id", None),  # assuming 'id' is the unique field
                defaults=item,
            )
        return Response(status=HTTP_200_OK)

    def get(self, request):
        if request.query_params.get("adatlap_id"):
            felmeres_items = models.FelmeresItems.objects.filter(
                adatlap_id=request.query_params.get("adatlap_id")
            ).annotate(
                coalesced_name=Coalesce(
                    "name", F("product_id__name"), output_field=CharField()
                ),
                sku=Coalesce("product_id__sku", Value(""), output_field=CharField()),
            )
            serializer = serializers.FelmeresItemsSerializer(felmeres_items, many=True)
            return Response(serializer.data)
        return super().get(request)


class FelmeresItemsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.FelmeresItems.objects.all()
    serializer_class = serializers.FelmeresItemsSerializer
    permission_classes = [AllowAny]


class OfferWebhook(APIView):
    def post(self, request):
        data = json.loads(request.body)
        log(
            "Penészmentesítés rendelés webhook meghívva",
            "INFO",
            "pen_offer_webhook",
            request.body,
        )
        try:
            if data["Data"]["Felmeresid"] is None:
                return Response("Succesfully received data", status=HTTP_200_OK)

            save_webhook(data["Data"])
            models.Offers(
                adatlap=models.MiniCrmAdatlapok.objects.get(Id=data["Id"]),
                id=data["Head"]["Id"],
            ).save()
            log(
                "Penészmentesítés rendelés webhook sikeresen lefutott",
                "SUCCESS",
                "pen_offer_webhook",
            )
            return Response("Succesfully received data", status=HTTP_200_OK)
        except:
            log(
                "Penészmentesítés ajánlat webhook sikertelen",
                "ERROR",
                "pen_offer_webhook",
                details=traceback.format_exc(),
            )
            return Response("Succesfully received data", status=HTTP_200_OK)


class QuestionProductsList(generics.ListCreateAPIView):
    queryset = models.QuestionProducts.objects.all()
    serializer_class = serializers.QuestionProductsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.query_params.get("product"):
            return models.QuestionProducts.objects.filter(
                product=self.request.query_params.get("product")
            )
        return super().get_queryset()

    def post(self, request):
        data = json.loads(request.body)
        question_instance = models.Questions.objects.get(id=data["question_id"])
        product_instance = models.Products.objects.get(id=data["product_id"])

        models.QuestionProducts.objects.create(
            question=question_instance, product=product_instance
        )
        return Response(status=HTTP_200_OK)

    def put(self, request):
        question_id = self.request.query_params.get("question_id")
        product_id = self.request.query_params.get("product")
        if question_id:
            products = models.QuestionProducts.objects.filter(question=question_id)
            products.delete()
            models.QuestionProducts.objects.bulk_create(
                [
                    models.QuestionProducts(
                        question=models.Questions.objects.get(id=question_id),
                        product=models.Products.objects.get(id=i),
                    )
                    for i in request.data
                ]
            )
            return Response(status=HTTP_200_OK)
        if product_id:
            questions = models.QuestionProducts.objects.filter(product=product_id)
            questions.delete()
            models.QuestionProducts.objects.bulk_create(
                [
                    models.QuestionProducts(
                        question=models.Questions.objects.get(id=i),
                        product=models.Products.objects.get(id=product_id),
                    )
                    for i in request.data
                ]
            )
            return Response(status=HTTP_200_OK)


class QuestionProductsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.QuestionProducts.objects.all()
    serializer_class = serializers.QuestionProductsSerializer
    permission_classes = [AllowAny]

    def get(self, request, pk):
        question_products = models.QuestionProducts.objects.filter(question=pk)
        serializer = serializers.QuestionProductsSerializer(
            question_products, many=True
        )
        return Response(serializer.data)


class UnasLogin(APIView):
    def post(self, request, type):
        log(
            "Unas login meghívva",
            "INFO",
            "pen_unas_login",
            request.body.decode("utf-8"),
        )
        response = request.body.decode("utf-8")
        root = ET.fromstring(response)
        for element in root.iter("ApiKey"):
            api_key = element.text
            if api_key.strip() == os.environ.get("CLOUD_API_KEY"):
                Login = ET.Element("Login")
                Token = ET.SubElement(Login, "Token")
                Token.text = "".join(
                    random.choices(
                        string.ascii_uppercase + string.ascii_lowercase + string.digits,
                        k=32,
                    )
                )
                with connection.cursor() as cursor:
                    cursor.execute("TRUNCATE pen_erp_auth_tokens")
                models.ErpAuthTokens(
                    token=Token.text,
                    expire=(
                        datetime.datetime.now() + datetime.timedelta(days=365 * 2)
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                ).save()

                Expire = ET.SubElement(Login, "Expire")
                Expire.text = (
                    datetime.datetime.now() + datetime.timedelta(days=365 * 2)
                ).strftime("%Y.%m.%d %H:%M:%S")

                ShopId = ET.SubElement(Login, "ShopId")
                ShopId.text = "119"

                Subscription = ET.SubElement(Login, "Subscription")
                Subscription.text = "vip-100000"

                Permissions = ET.SubElement(Login, "Permissions")
                permission_items = ["getOrder", "setProduct"]
                for item in permission_items:
                    permission_sub = ET.SubElement(Permissions, "Permission")
                    permission_sub.text = item

                Status = ET.SubElement(Login, "Status")
                Status.text = "ok"

                response = '<?xml version="1.0" encoding="UTF-8" ?>\n' + ET.tostring(
                    Login, encoding="unicode"
                )
                return HttpResponse(response, status=HTTP_200_OK)
            return Response("Hibás API kulcs", status=HTTP_401_UNAUTHORIZED)


def get_unas_order_data(type):
    adatlapok = models.MiniCrmAdatlapok.objects.filter(
        Q(Enum1951=4374) | Q(StatusId=3008), CategoryId=29, Deleted="0"
    ).values()
    if not adatlapok:
        return """<?xml version="1.0" encoding="UTF-8" ?>
                            <Orders>
                            </Orders>"""

    datas = []
    for adatlap in adatlapok:
        if adatlap["RendelesSzama"] != "" and adatlap["RendelesSzama"] is not None:
            continue
        # Get the order data, adatlap details, business contact details, address, and contact details for each adatlap
        order_data = models.Orders.objects.get(adatlap_id=adatlap["Id"]).__dict__
        script_name = "pen_unas_get_order"
        kapcsolat = contact_details(
            contact_id=adatlap["ContactId"],
            script_name=script_name,
            description="Vevő adatok",
        )
        if kapcsolat["status"] == "Error":
            log(
                "Hiba akadt a kontaktok lekérdezése közben",
                "ERROR",
                script_name,
                details=kapcsolat["response"],
            )
            return f"<Error>{kapcsolat['response']}</Error>"
        kapcsolat = kapcsolat["response"]
        if adatlap["MainContactId"] != adatlap["ContactId"]:
            business_kapcsolat = contact_details(
                contact_id=adatlap["MainContactId"],
                script_name=script_name,
                description="Számlázási adatok",
            )
            if business_kapcsolat["status"] == "Error":
                log(
                    "Hiba akadt a kontaktok lekérdezése közben",
                    "ERROR",
                    script_name,
                    business_kapcsolat["response"],
                )
                return f"<Error>{business_kapcsolat['response']}</Error>"
            business_kapcsolat = business_kapcsolat["response"]
        else:
            business_kapcsolat = {
                "Name": (
                    kapcsolat["LastName"] + " " + kapcsolat["FirstName"]
                    if not kapcsolat.get("Name")
                    else kapcsolat.get("Name")
                ),
                "EUVatNumber": "",
                **kapcsolat,
            }

        try:
            cim = address_details(
                list(
                    address_ids(
                        adatlap["MainContactId"],
                        script_name=script_name,
                        description="Cím lista",
                    )
                )[0],
                script_name=script_name,
                description="Cím részlet",
            )
        except:
            ids = list(
                address_ids(
                    adatlap["ContactId"],
                    script_name=script_name,
                    description="Cím lista",
                )
            )
            if ids:
                cim = address_details(
                    ids[0], script_name=script_name, description="Cím részlet"
                )
            else:
                cim = {
                    "PostalCode": "",
                    "City": "",
                    "Address": "",
                    "County": "",
                    "CountryId": "",
                    "Country": "",
                }

        felmeres = models.Felmeresek.objects.filter(
            id=adatlap["FelmeresLink"].split("/")[-1] if adatlap["FelmeresLink"] else 0
        ).first()
        if felmeres is None:
            log("Nem található felmérés", "ERROR", script_name, adatlap["Id"])
            continue
        print(felmeres)

        # Add the data to the datas list

        datas.append(
            {
                "OrderData": order_data,
                "AdatlapDetails": adatlap,
                "FelmeresAdatlapDetails": felmeres.adatlap_id,
                "BusinessKapcsolat": business_kapcsolat,
                "Cím": cim["response"],
                "Kapcsolat": kapcsolat,
                "Tételek": list(
                    models.FelmeresItems.objects.filter(
                        adatlap_id=felmeres.id if felmeres else 0
                    )
                ),
                "Munkadíj": sum(
                    [
                        i.value * i.amount
                        for i in models.FelmeresMunkadijak.objects.filter(
                            felmeres=felmeres.id if felmeres else 0
                        )
                    ]
                ),
            }
        )

    return (
        """<?xml version="1.0" encoding="UTF-8" ?>
    <Orders> """
        + "\n".join(
            [
                f"""<Order>
            <Key>{data["OrderData"]["order_id"] if type != "dev" else str(uuid.uuid4())}</Key>
            <Date>{data["AdatlapDetails"]["CreatedAt"].strftime('%Y.%m.%d %H:%M:%S')}</Date>
            <DateMod>{data["AdatlapDetails"]["CreatedAt"].strftime('%Y.%m.%d %H:%M:%S')}</DateMod>
            <Lang>hu</Lang>
            <Customer>
                <Id>{data["Kapcsolat"]["Id"]}</Id>
                <Email>{data["Kapcsolat"]["Email"]}</Email>
                <Username>{data["Kapcsolat"]["LastName"] + " " + data["Kapcsolat"]["FirstName"]}</Username>
                <Contact>
                    <Name>{data["Kapcsolat"]["LastName"] + " " + data["Kapcsolat"]["FirstName"]}</Name>
                    <Phone>{data["Kapcsolat"]["Phone"]}</Phone>
                    <Mobile>{data["Kapcsolat"]["Phone"]}</Mobile>
                    <Lang>hu</Lang>
                </Contact>
                <Addresses>
                    <Invoice>
                        <Name>{data["BusinessKapcsolat"]["Name"]}</Name>
                        <ZIP>{data["Cím"]["PostalCode"]}</ZIP>
                        <City>{data["Cím"]["City"]}</City>
                        <Street>{data["Cím"]["Address"]}</Street>
                        <County>{data["Cím"]["County"]}</County>
                        <Country>{data["Cím"]["CountryId"]}</Country>
                        <CountryCode>hu</CountryCode>
                        <TaxNumber>{data["BusinessKapcsolat"]["VatNumber"]}</TaxNumber>
                        <EUTaxNumber>{data['BusinessKapcsolat']["EUVatNumber"] if data['BusinessKapcsolat']["EUVatNumber"] else ""}</EUTaxNumber>
                        <CustomerType>private</CustomerType>
                    </Invoice>
                    <Shipping>
                        <Name>{data["Kapcsolat"]["LastName"]} {data["Kapcsolat"]["FirstName"]}</Name>
                        <ZIP>{data["FelmeresAdatlapDetails"].Iranyitoszam}</ZIP>
                        <City>{data["FelmeresAdatlapDetails"].Telepules}</City>
                        <Street>{data["FelmeresAdatlapDetails"].Cim2}</Street>
                        <County>{data["FelmeresAdatlapDetails"].Megye}</County>
                        <Country>{data["FelmeresAdatlapDetails"].Orszag}</Country>
                    <CountryCode>hu</CountryCode>
                        <DeliveryPointID>6087-NOGROUPGRP</DeliveryPointID>
                        <DeliveryPointGroup>gls_hu_dropoffpoints</DeliveryPointGroup>
                        <RecipientName>{data["Kapcsolat"]["LastName"]} {data["Kapcsolat"]["FirstName"]}</RecipientName>
                    </Shipping>
                </Addresses>
            </Customer>
            <Currency>HUF</Currency>
            <Status>Folyamatban</Status>
            <StatusDateMod><![CDATA[2021.03.25 20:15:39]]></StatusDateMod>
            <StatusID>3008</StatusID>
            <Payment>
                <Id>{models.PaymentMethods.objects.get(name=data["AdatlapDetails"]["FizetesiMod3"]).id if data["AdatlapDetails"]["FizetesiMod3"] else ""}</Id>
                <Name>{data["AdatlapDetails"]["FizetesiMod3"]}</Name>
                <Type>transfer</Type>
            </Payment>
            <Shipping>
                <Id>3372937</Id>
                <Name><![CDATA[GLS CsomagPontok]]></Name>
            </Shipping>
            <SumPriceGross>{sum([(float(i.netPrice) if i.valueType != "percent" else (get_total(data) * (int(i.netPrice)/100) if i.type != 'Discount' else -(get_total(data) * (int(i.netPrice)/100)))) * sum([j["ammount"] for j in i.inputValues]) for i in data["Tételek"]])*1.27}</SumPriceGross>
            <Items>
                """
                + "\n".join(
                    [
                        f"""<Item>
                    <Id>{i.product_id if i.product_id else "discount-amount"}</Id>
                    <Sku>{i.product.sku if i.product else "discount-amount"}</Sku>
                    <Name>{i.name}</Name>
                    <Unit>darab</Unit>
                    <Quantity>{sum([float(j["ammount"]) for j in i.inputValues])}</Quantity>
                    <PriceNet>{"-" if i.type == "Discount" else ""}{float(i.netPrice) if i.valueType != "percent" else get_total(data) * (int(i.netPrice)/100)}</PriceNet>
                    <PriceGross>{"-" if i.type == "Discount" else ""}{(float(i.netPrice) if i.valueType != "percent" else get_total(data) * (int(i.netPrice)/100))*1.27}</PriceGross>
                    <Vat>27%</Vat>
                    <Status>
                        <![CDATA[]]>
                    </Status>
                    </Item>
                    """
                        for i in data["Tételek"]
                    ]
                )
                + """
                """
                + (
                    f"""
                <Item>
                    <Id>discount-amount</Id>
                    <Sku>discount-amount</Sku>
                    <Name>Munkadíj</Name>
                    <Unit>darab</Unit>
                    <Quantity>1</Quantity>
                    <PriceNet>{data["Munkadíj"]}</PriceNet>
                    <PriceGross>{data["Munkadíj"]*1.27}</PriceGross>
                    <Vat>27%</Vat>
                    <Status>
                        <![CDATA[]]>
                    </Status>
                    </Item>
                    """
                    if data["Munkadíj"]
                    else ""
                )
                + """
            </Items>
            <Params>
"""
                + "\n".join(
                    [
                        f"""<Param>
<Id>{index}</Id>
<Name><![CDATA[clouderp-labels]]></Name>
<Value><![CDATA[{i}]]></Value>
</Param>"""
                        for index, i in enumerate(
                            data["AdatlapDetails"]["Beepitok"].split(", ")
                        )
                    ]
                )
                + """
            </Params>
        </Order> """
                for index, data in enumerate(datas)
                if type != "dev" or index == 0
            ]
        )
        + """
        </Orders>
    """
    )


def get_total(data):
    total = (
        sum(
            [
                float(i.netPrice) * sum([j["ammount"] for j in i.inputValues])
                for i in data["Tételek"]
                if i.valueType != "percent"
            ]
        )
        + data["Munkadíj"]
    )

    return total


class UnasGetOrder(APIView):
    parser_classes = (XMLParser,)
    renderer_classes = (XMLRenderer,)

    def post(self, request, type):
        log(
            "Unas rendelések lekérdezése meghívva",
            "INFO",
            "pen_unas_get_order",
            request.body.decode("utf-8"),
        )
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header[7:]
                token = models.ErpAuthTokens.objects.get(token=token)
                if token.expire > datetime.datetime.now():
                    response = get_unas_order_data(type)
                    return HttpResponse(response, status=HTTP_200_OK)
                else:
                    return Response("Token lejárt", status=HTTP_401_UNAUTHORIZED)
            except Exception as e:
                log(
                    "Unas rendelések lekérdezése sikertelen. Error: "
                    + str(e)
                    + ". Traceback: "
                    + traceback.format_exc(),
                    "ERROR",
                    "pen_unas_get_order",
                )
                return Response(str(e), status=HTTP_401_UNAUTHORIZED)
        return Response("Hibás Token", status=HTTP_401_UNAUTHORIZED)

    def get(self, request, type):
        if os.environ.get("ENVIRONMENT") == "development":
            log(
                "Unas rendelések lekérdezése meghívva",
                "INFO",
                "pen_unas_get_order_dev",
                request.body.decode("utf-8"),
            )
            response = get_unas_order_data(type)
            return HttpResponse(response, HTTP_200_OK)
        log(
            "Unas rendelések lekérdezése sikertelen",
            "ERROR",
            "pen_unas_get_order",
            "Nem development környezetben fut",
        )


class UnasSetProduct(APIView):
    parser_classes = (XMLParser,)
    renderer_classes = (XMLRenderer,)

    def post(self, request, type):
        log(
            "Unas termék szinkron megkezdődött",
            "INFO",
            "pen_unas_set_product",
            request.body.decode("utf-8"),
        )
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header[7:]
                token = models.ErpAuthTokens.objects.get(token=token)
                if token.expire > datetime.datetime.now():
                    xml_string = request.body.decode("utf-8")
                    self_closing_tags = ["br", "img", "input", "hr", "meta", "link"]
                    for tag in self_closing_tags:
                        pattern = re.compile(r"<({})([^<>]*)>".format(tag))
                        xml_string = pattern.sub(replace_self_closing_tags, xml_string)
                    root = ET.fromstring(xml_string)
                    products = [
                        {
                            "id": element.find("local_id").text,
                            "sku": (
                                element.find("Sku").text if element.find("Sku") else ""
                            ),
                        }
                        for element in root.iter("Product")
                        if element
                    ]
                    response = (
                        """<?xml version="1.0" encoding="UTF-8" ?>
            <Products>
                """
                        + "\n".join(
                            [
                                f"""
                <Product>
                    <Id>{product["id"]}</Id>
                    <Sku>{product["sku"]}</Sku>
                    <Action>add</Action>
                    <Status>ok</Status>
                </Product>"""
                                for product in products
                            ]
                        )
                        + """
            </Products>"""
                    )
                    return HttpResponse(response, status=HTTP_200_OK)
                else:
                    return Response("Token lejárt", status=HTTP_401_UNAUTHORIZED)
            except Exception as e:
                log(
                    "Unas rendelések lekérdezése sikertelen",
                    "ERROR",
                    "pen_unas_set_product",
                    details=traceback.format_exc(),
                )
                return Response("Hibás Token " + str(e), status=HTTP_401_UNAUTHORIZED)
        return Response("Hibás Token", status=HTTP_401_UNAUTHORIZED)


class FilterItemsList(generics.ListCreateAPIView):
    queryset = models.FilterItems.objects.all()
    serializer_class = serializers.FilterItemsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.query_params.get("filter"):
            return models.FilterItems.objects.filter(
                filter=self.request.query_params.get("filter")
            )
        return super().get_queryset()

    def post(self, request):
        data = request.data
        if isinstance(data, list):
            items = []
            for item in data:
                filter_id = item.pop("filter", None)
                if filter_id is not None:
                    item["filter"] = models.Filters.objects.get(id=filter_id)
                items.append(models.FilterItems(**item))
            models.FilterItems.objects.bulk_create(items)
            return Response({"status": "success"}, status=HTTP_201_CREATED)
        else:
            return Response(
                {"status": "bad request", "message": "Expected a list of items"},
                status=HTTP_400_BAD_REQUEST,
            )


class FilterItemsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.FilterItems.objects.all()
    serializer_class = serializers.FilterItemsSerializer
    permission_classes = [AllowAny]


class CancelOffer(APIView):
    def post(self, request):
        log(
            "MiniCRM ajánlat sztornózása megkezdődött",
            "INFO",
            "pen_cancel_offer",
            request.body.decode("utf-8"),
        )

        adatlap = models.MiniCrmAdatlapok.objects.filter(
            Felmeresid=request.data["adatlap_id"]
        )
        if not adatlap.exists():
            log("Nem található adatlap", "ERROR", "pen_cancel_offer")
            return Response("Nem található adatlap", HTTP_400_BAD_REQUEST)
        offer = models.Offers.objects.filter(adatlap=adatlap.first().Id)
        if not offer.exists():
            log("Nem található ajánlat", "ERROR", "pen_cancel_offer")
            return Response("Nem található ajánlat", HTTP_400_BAD_REQUEST)
        update_resp = update_offer_order(
            offer_id=offer.first().id,
            fields={"StatusId": "Sztornózva"},
            project=True,
        )
        if update_resp.status_code != 200:
            log(
                "MiniCRM ajánlat sztornózása sikertelen",
                "ERROR",
                "pen_cancel_offer",
                update_resp.text,
                {"adatlap_id": request.data["adatlap_id"]},
            )
            return Response(update_resp.text, HTTP_400_BAD_REQUEST)
        models.Felmeresek.objects.filter(id=request.data["adatlap_id"]).update(
            status="CANCELLED"
        )
        return Response("Sikeres sztornózás", HTTP_200_OK)


@csrf_exempt
def upload_file(request):
    if request.method == "POST":
        files = request.FILES.getlist("files")
        if not files:
            return JsonResponse({"success": False}, status=400)

        s3_client = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        try:
            felmeres_id = request.GET.get("felmeres_id")
            for file in files:
                new_file_name = f"{felmeres_id}{file.name}"
                s3_client.upload_fileobj(
                    file,
                    os.getenv("AWS_BUCKET_NAME"),
                    new_file_name,
                    ExtraArgs={"ACL": "public-read", "ContentType": file.content_type},
                )
            return JsonResponse(
                {
                    "success": True,
                    "async_id_symbol": json.dumps([file.name for file in files]),
                },
                status=200,
            )
        except Exception as e:
            log(
                "Hiba akadt a képfeltöltés közben",
                "ERROR",
                "pen_upload_file",
                traceback.format_exc(),
            )
            return JsonResponse({"success": False}, status=500)
    return JsonResponse({"success": False}, status=400)


class FelmeresPicturesList(generics.ListCreateAPIView):
    serializer_class = serializers.FelmeresPicturesSerializer
    queryset = models.FelmeresPictures.objects.all()
    permission_classes = [AllowAny]

    def get_queryset(self):
        return get_queryset_from_felmeres(self, models.FelmeresPictures)


class FelmeresPicturesDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.FelmeresPicturesSerializer
    queryset = models.FelmeresPictures.objects.all()
    permission_classes = [AllowAny]

    def delete(self, request, pk):
        file = models.FelmeresPictures.objects.get(id=pk)
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            region_name=os.environ.get("AWS_REGION"),
        )
        s3_client.delete_object(
            Bucket=os.environ.get("AWS_BUCKET_NAME"), Key=file.src.split("/")[-1]
        )
        file.delete()
        return Response("Sikeresen törlésre került", status=HTTP_200_OK)


class FelmeresNotesList(generics.ListCreateAPIView):
    serializer_class = serializers.FelmeresNotesSerializer
    queryset = models.FelmeresekNotes.objects.all()
    permission_classes = [AllowAny]

    def get_queryset(self):
        return get_queryset_from_felmeres(self, models.FelmeresekNotes)

    def patch(self, request):
        data = request.data
        felmeres_id = request.query_params.get("felmeres_id")
        models.FelmeresekNotes.objects.filter(felmeres_id=felmeres_id).update(**data)
        return Response(status=HTTP_200_OK)


class FelmeresNotesDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.FelmeresNotesSerializer
    queryset = models.FelmeresekNotes.objects.all()
    permission_classes = [AllowAny]


def get_queryset_from_felmeres(self, model):
    if self.request.query_params.get("felmeres_id"):
        return model.objects.filter(
            felmeres_id=self.request.query_params.get("felmeres_id")
        )
    return model.objects.all()


class UserRole(APIView):
    def get(self, request, user):
        try:
            user_role = models.UserRoles.objects.get(user=user).role
            return Response(serializers.RolesSerializer(user_role).data)
        except models.UserRoles.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)


class MiniCrmAdatlapok(APIView):

    def get(self, request):
        queryset = models.MiniCrmAdatlapok.objects.all()

        # Filtering
        id = request.query_params.get("Id")
        if id:
            id = id.split(",")
            queryset = queryset.filter(Id__in=id)
        status_id = request.query_params.get("StatusId")
        if status_id:
            status_id = status_id.split(",")
            queryset = queryset.filter(StatusId__in=status_id)
        if request.query_params.get("CategoryId"):
            queryset = queryset.filter(
                CategoryId=request.query_params.get("CategoryId")
            )

        adatlapok = []
        for i in queryset.values(
            "Id",
            "Name",
            "CategoryId",
            "StatusId",
            "ContactId",
            "FelmeresiDij",
            "Telepules",
            "Iranyitoszam",
            "Orszag",
            "Felmero2",
            "IngatlanKepe",
            "CreatedAt",
            "Cim2",
            "Beepitok",
            "DateTime1953",
            "KiMerteFel2",
            "FelmeresDatuma2",
            "RendelesSzama",
            "FelmeresLink",
            "MainContactId",
        ):
            try:
                felmeres_id = int(i["FelmeresLink"].split("/")[-1])
                felmeres = models.Felmeresek.objects.filter(id=felmeres_id)
                if felmeres.exists():
                    felmeres = felmeres.first()
                    i["NetTotal"] = felmeres.netOrderTotal
                    i["Tavolsag"] = felmeres.adatlap_id.Tavolsag
                    i["FelmeresCim"] = get_address(felmeres.adatlap_id)
                    contact = contact_details(i["ContactId"])
                    if contact != "Error":
                        contact = contact["response"]
                        i["Phone"] = contact["Phone"]
                        i["Email"] = contact["Email"]
                else:
                    i["NetTotal"] = 0
                    i["FelmeresCim"] = ""
            except:
                i["NetTotal"] = 0
                i["FelmeresCim"] = ""

            adatlapok.append(i)

        return Response(adatlapok)


class MiniCrmAdatlapokDetail(generics.RetrieveAPIView):
    serializer_class = serializers.MiniCrmAdatlapokSerializer
    queryset = models.MiniCrmAdatlapok.objects.all()
    permission_classes = [AllowAny]


class MunkadijList(generics.ListCreateAPIView):
    serializer_class = serializers.MunkadijSerializer
    queryset = models.Munkadij.objects.all()
    permission_classes = [AllowAny]
    filterset_fields = "__all__"


class MunkadijDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.MunkadijSerializer
    queryset = models.Munkadij.objects.all()
    permission_classes = [AllowAny]

    def delete(self, request, pk):
        try:
            models.Munkadij.objects.filter(id=pk).delete()
            models.ProductTemplate.objects.filter(product=pk, type="Munkadíj").delete()
            return Response(status=HTTP_200_OK)
        except:
            return Response(status=HTTP_400_BAD_REQUEST)


class FelmeresMunkadijList(generics.ListCreateAPIView):
    serializer_class = serializers.FelmeresMunkadijakSerializer
    queryset = models.FelmeresMunkadijak.objects.all()
    permission_classes = [AllowAny]
    filterset_fields = "__all__"

    def post(self, request):
        data = request.data
        adatlap_ids_in_request = [item.get("felmeres") for item in data]

        # Delete items not in request
        models.FelmeresMunkadijak.objects.filter(
            felmeres__in=adatlap_ids_in_request
        ).delete()

        for item in data:
            adatlap_id = item.pop("felmeres", None)
            munkadij_id = item.pop("munkadij", None)
            if adatlap_id is not None:
                adatlap = get_object_or_404(models.Felmeresek, id=adatlap_id)
                item["felmeres"] = adatlap
            if munkadij_id is not None:
                product = get_object_or_404(models.Munkadij, id=munkadij_id)
                item["munkadij"] = product
            item = {
                k: v
                for k, v in item.items()
                if k in [f.name for f in models.FelmeresMunkadijak._meta.get_fields()]
            }
            instance, created = models.FelmeresMunkadijak.objects.update_or_create(
                id=item.get("id", None),  # assuming 'id' is the unique field
                defaults=item,
            )
        return Response(status=HTTP_200_OK)


class FelmeresMunkadijDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.FelmeresMunkadijakSerializer
    queryset = models.FelmeresMunkadijak.objects.all()
    permission_classes = [AllowAny]


class SettingsList(generics.ListAPIView):
    serializer_class = serializers.SettingsSerializer
    queryset = models.Settings.objects.all()
    permission_classes = [AllowAny]


class MiniCrmProxy(APIView):
    def put(self, request, adatlap_id):
        data = mini_crm_proxy(request.data, adatlap_id, True)
        if data["code"] == 200:
            return Response(data["data"])
        else:
            return Response(data=data["reason"], status=data["code"])


class GaranciaWebhook(APIView):
    def post(self, request):
        adatlap = json.loads(request.body)
        log("Garancia webhook meghívva", "INFO", "pen_garancia_webhook", data=adatlap)
        adatlap = map_wh_fields(
            adatlap, {"BejelentesTipusa", "GaranciaFelmerestVegzi", "FizetesiMod4"}
        )["Data"]
        save_webhook(adatlap, name="garancia")

        if (
            adatlap["StatusId"] == "3121"
            and adatlap["UtvonalAKozponttol2"] is None
            and adatlap["BejelentesTipusa"] != "Kapcsolat"
        ):

            def update_data(duration, distance, fee, street_view_url, county, address):
                return {
                    "UtazasiIdoKozponttol2": duration,
                    "TavolsagKm": distance,
                    "NettoFelmeresiDij": fee,
                    "BruttoFelmeresiDij2": round(fee * 1.27),
                    "UtvonalAKozponttol2": f"https://www.google.com/maps/dir/?api=1&origin=Nagytétényi+út+218,+Budapest,+1225&destination={address}&travelmode=driving",
                    "Megye3": county,
                    "KarbantartasNettoDij": 20000,
                }

            response = calculate_distance_fn(
                adatlap,
                address=lambda x: f"{x['Cim3']} {x['Telepules2']}, {x['Iranyitoszam2']} {x['Orszag2']}",
                city_field="Telepules2",
                update_data=update_data,
            )
            if response == "Error":
                return Response({"status": "error"}, status=HTTP_200_OK)
        return Response({"status": "success"}, status=HTTP_200_OK)


class Slots(APIView):
    def get(self, request, external_id):
        slots = models.Slots.objects.filter(external_id=external_id)
        for slot in slots:
            best_slot = models.BestSlots.objects.filter(slot=slot.id)
            if best_slot.exists():
                slot.level = best_slot.first().level
        return Response(serializers.SlotSerializer(slots, many=True).data)

    def post(self, request, external_id):
        booked_slots = models.Slots.objects.filter(external_id=external_id)
        booked_slots.exclude(id__in=request.data).update(booked=False)
        booked_slots.filter(id__in=request.data).update(booked=True)
        return Response(status=HTTP_200_OK)


class SchedulerSettings(generics.ListAPIView):
    serializer_class = serializers.SchedulerSettingsSerializer
    queryset = models.SchedulerSettings.objects.all()
    permission_classes = [AllowAny]
    filterset_fields = "__all__"


import requests
from rest_framework.decorators import api_view


@csrf_exempt
@api_view(["POST"])
def minicrm_proxy(request):
    data = request.body.decode("utf-8")
    log(
        "Minicrm proxy meghívva",
        "INFO",
        "pen_minicrm_proxy",
        data,
    )
    endpoint = request.GET.get("endpoint")

    if endpoint == "XML":
        system_id = os.environ.get("PEN_MINICRM_SYSTEM_ID")
        api_key = os.environ.get("PEN_MINICRM_API_KEY")

        response = requests.post(
            f"https://r3.minicrm.hu/Api/SyncFeed/119/Upload",
            auth=(system_id, api_key),
            data=data.encode("utf-8"),
            headers={"Content-Type": "application/xml"},
        )

        if response.ok:
            log("Minicrm proxy sikeres", "INFO", "pen_minicrm_proxy", response.text)
            return Response(response.json())
        else:
            log(
                "Minicrm proxy sikertelen",
                "ERROR",
                "pen_minicrm_proxy",
                response.text,
            )
            return Response({"error": "Error " + response.text}, status=400)
    log("Minicrm proxy sikertelen", "ERROR", "pen_minicrm_proxy", "Missing endpoint")
    return Response({"error": "Missing endpoint"}, status=400)
