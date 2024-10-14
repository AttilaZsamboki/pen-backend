import datetime
import json
import os
import random
import re
import string
import traceback
import uuid
import xml.etree.ElementTree as ET
from functools import partial

# Create your views here.
from typing import Dict, List

import boto3
import requests
from django.db import connection
from django.db.models import CharField, Q, Value, OuterRef, Subquery, F
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
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

from .utils.logs import log
from . import models, serializers
from .auth0backend import CustomJWTAuthentication
from .utils.calculate_distance import CalculateDistance
from .utils.minicrm import Address, Contact, MiniCrmClient
from .utils.utils import replace_self_closing_tags
from .services.minicrm import MiniCRMWrapper
from functools import wraps


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


def set_system(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            system_id = data.get("Data").get("SystemId")
            if not system_id:
                return JsonResponse({"error": "SystemId not provided"}, status=400)
            system = models.Systems.objects.get(system_id=system_id)
            minicrm_wrapper = MiniCRMWrapper(system=system)
            for attr in dir(minicrm_wrapper):
                if not attr.startswith("__") and not callable(
                    getattr(minicrm_wrapper, attr)
                ):
                    setattr(self, attr, getattr(minicrm_wrapper, attr))
        except models.Systems.DoesNotExist:
            return JsonResponse({"error": "System not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        return func(self, request, *args, **kwargs)

    return wrapper


def save_webhook(adatlap, process_data=None, _="felmeres", system=None):
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
    mapped_data = {
        models.SystemSettings.objects.filter(label=k, system=system).first().value: v
        for k, v in filtered_data.items()
        if models.SystemSettings.objects.filter(label=k, system=system).exists()
    }

    models.MiniCrmAdatlapok(
        **mapped_data,
    ).save()
    return adatlap


class BaseAPIView(APIView):
    script_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.script_name is None:
            self.script_name = self.__class__.__name__
        self.log = partial(log, script_name=self.script_name)


class MiniCrmAPIView(BaseAPIView):
    mini_crm_client = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mini_crm_client = MiniCrmClient(
            os.environ.get("PEN_MINICRM_SYSTEM_ID"),
            os.environ.get("PEN_MINICRM_API_KEY"),
            script_name=self.script_name,
        )


class FelmeresWebhook(APIView):

    @set_system
    def post(self, request):
        data = json.loads(request.body)
        log(
            "Felmérés webhook meghívva",
            "INFO",
            "pen_felmeres_webhook",
            data=data,
            system_id=self.system.system_id,
        )
        data = map_wh_fields(
            data,
            ["Felmero2", "FizetesiMod2", "SzamlazasIngatlanCimre2"],
        )["Data"]

        save_webhook(data, self.system)

        if (
            data["StatusId"]
            == models.SystemSettings.objects.get(label="Új érdeklődő").value
            and data[models.Settings.objects.get(label="UtvonalAKozponttol").value]
            is None
        ):

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

            response = CalculateDistance(self.system).fn(
                data,
                address=lambda x: x.FullAddress,
                update_data=update_data,
            )
            if response == "Error":
                return Response({"status": "error"}, status=HTTP_200_OK)
        return Response({"status": "success"}, status=HTTP_200_OK)

    def get(self, _):
        log(
            "Penészmentesítés webhook meghívva de 'GET' methoddal",
            "INFO",
            "pen_calculate_distance",
        )
        return Response({"status": "error"}, status=HTTP_405_METHOD_NOT_ALLOWED)


class FilterByQueryParamMixin:
    filter_param = None
    filter_field = None

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_value = self.request.query_params.get(self.filter_param)
        if filter_value is not None:
            filter_kwargs = {self.filter_field: filter_value}
            queryset = queryset.filter(**filter_kwargs)
        return queryset


class FilterByQueryParamsMixin:
    filter_params = {}

    def get_queryset(self):
        queryset = super().get_queryset()
        for param, field in self.filter_params.items():
            filter_value = self.request.query_params.get(param)
            if filter_value is not None:
                filter_kwargs = {field: filter_value}
                queryset = queryset.filter(**filter_kwargs)
        return queryset


class FilterBySystemIdMixin(FilterByQueryParamMixin):
    filter_param = "system_id"
    filter_field = "system_id"


class FilterBySystemAndFelmeresIdMixin(FilterByQueryParamsMixin):
    filter_params = {
        "system_id": "system_id",
        "felmeres_id": "felmeres_id",
    }


class FelmeresQuestionsList(generics.ListCreateAPIView):
    queryset = models.FelmeresQuestions.objects.all()
    serializer_class = serializers.FelmeresQuestionsSerializer
    permission_classes = [AllowAny]


class FelmeresQuestionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.FelmeresQuestions.objects.all()
    serializer_class = serializers.FelmeresQuestionsSerializer

    def get(self, _, pk):
        felmeres = models.FelmeresQuestions.objects.filter(adatlap_id=pk)
        serializer = serializers.FelmeresQuestionsSerializer(felmeres, many=True)
        return Response(serializer.data)


class OrderWebhook(APIView):
    @set_system
    def post(self, request):
        data = json.loads(request.body)
        log(
            "Penészmentesítés rendelés webhook meghívva",
            "INFO",
            "pen_order_webhook",
            json.dumps(data),
            system_id=self.system.system_id,
        )
        try:
            beepitok = models.SystemSettings.objects.get(label="Beepitok").value
            name_mapping = data["Schema"][beepitok]

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
                    "Enum1951",
                ],
            )

            def process_data(data):
                data[beepitok] = ", ".join(get_names(data[beepitok]))
                return data

            save_webhook(data["Data"], process_data=process_data)

            if not models.Orders.objects.filter(
                adatlap_id=data["Id"], order_id=data["Head"]["Id"], system=self.system
            ).exists():
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


class ProductsList(FilterByQueryParamMixin, generics.ListCreateAPIView):
    queryset = models.Products.objects.all()
    serializer_class = serializers.ProductsSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination
    filter_field = "system_id"
    filter_param = "system_id"

    def get(self, request, *args, **kwargs):
        all = request.query_params.get("all", "false")
        if all.lower() == "true":
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
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


class ProductAttributesList(FilterBySystemIdMixin, generics.ListCreateAPIView):
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


class FiltersList(FilterBySystemIdMixin, generics.ListCreateAPIView):
    queryset = models.Filters.objects.all()
    serializer_class = serializers.FiltersSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        type_param = self.request.query_params.get("type")
        user_param = self.request.query_params.get("user")

        if type_param or user_param:
            filters = {}
            if type_param:
                filters["type"] = type_param
            if user_param:
                filters["user"] = user_param
            return queryset.filter(**filters)
        else:
            return queryset.all()


class FiltersDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Filters.objects.all()
    serializer_class = serializers.FiltersSerializer
    permission_classes = [AllowAny]


class QuestionsList(FilterBySystemIdMixin, generics.ListCreateAPIView):
    queryset = models.Questions.objects.all()
    serializer_class = serializers.QuestionsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get("product"):
            question_id = queryset.filter(
                product=self.request.query_params.get("product")
            ).values("question")[0]["question"]
            return queryset.filter(id=question_id)
        elif self.request.query_params.get("connection"):
            return queryset.filter(
                connection=self.request.query_params.get("connection")
            )
        return queryset


class QuestionsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Questions.objects.all()
    serializer_class = serializers.QuestionsSerializer
    permission_classes = [AllowAny]


class TemplateList(FilterBySystemIdMixin, generics.ListCreateAPIView):
    queryset = models.Templates.objects.all()
    serializer_class = serializers.TemplatesSerializer
    permission_classes = [AllowAny]


class TemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Templates.objects.all()
    serializer_class = serializers.TemplatesSerializer
    permission_classes = [AllowAny]


class ProductTemplatesList(FilterBySystemIdMixin, generics.ListCreateAPIView):
    queryset = models.ProductTemplate.objects.all()
    serializer_class = serializers.ProductTemplateSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        queryset = super().get_queryset()
        template_id = self.request.query_params.get("template_id")
        products = queryset.filter(template=template_id)
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


class FelmeresekList(FilterBySystemIdMixin, generics.ListCreateAPIView):
    queryset = models.Felmeresek.objects.all()
    serializer_class = serializers.FelmeresekSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filterset_fields = ["adatlap_id"]
    ordering_fields = "__all__"
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
    payload = {
        "adatlap_id": felmeres.adatlap_id,
        "felmeres_total": felmeres.netOrderTotal,
        **felmeres.__dict__,
    }
    offer_adatlap = models.MiniCrmAdatlapok.objects.filter(Felmeresid=pk)
    if offer_adatlap.exists():
        offer_adatlap = offer_adatlap.first()
        payload["offer_status"] = offer_adatlap.StatusIdStr

    return serializers.FelmeresekSerializer(payload)


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
                "FAILED",
                "pen_felmeresek_detail",
                details=f"Error: {e}. {traceback.format_exc()}",
            )
            return Response("A felmérés nem létezik", status=HTTP_400_BAD_REQUEST)


class FelmeresItemsList(FilterBySystemIdMixin, generics.ListCreateAPIView):
    queryset = models.FelmeresItems.objects.all()
    permission_classes = [AllowAny]
    serializer_class = serializers.FelmeresItemsSerializer

    def post(self, request):

        def filter_item_fields(item):
            valid_fields = [f.name for f in models.FelmeresItems._meta.get_fields()]
            return {k: v for k, v in item.items() if k in valid_fields}

        def create_or_update_item(item):
            adatlap_id = item.pop("adatlap", None)
            product_id = item.pop("product", None)
            if adatlap_id is not None:
                item["adatlap"] = get_object_or_404(models.Felmeresek, id=adatlap_id)
            if product_id is not None:
                item["product"] = get_object_or_404(models.Products, id=product_id)
            item = filter_item_fields(item)
            instance, _ = models.FelmeresItems.objects.update_or_create(
                id=item.get("id", None),
                defaults=item,
            )
            return instance

        data = request.data
        adatlap_ids_in_request = list(map(lambda i: i.get("adatlap"), data))

        models.FelmeresItems.objects.filter(
            adatlap_id__in=adatlap_ids_in_request
        ).delete()

        instances = list(map(lambda i: create_or_update_item(i), data))

        return Response(
            data=serializers.FelmeresItemsSerializer(instances, many=True).data,
            status=HTTP_200_OK,
        )

    def get(self, request):
        queryset = super().get_queryset()
        if request.query_params.get("adatlap_id"):
            product_subquery = models.Products.objects.filter(
                id=OuterRef("product_id")
            ).values("name", "sku")[:1]

            felmeres_items = queryset.filter(
                adatlap_id=request.query_params.get("adatlap_id")
            ).annotate(
                coalesced_name=Coalesce(
                    "name",
                    Subquery(product_subquery.values("name")),
                    output_field=CharField(),
                ),
                sku=Coalesce(
                    Subquery(product_subquery.values("sku")),
                    Value(""),
                    output_field=CharField(),
                ),
            )
            serializer = serializers.FelmeresItemsSerializer(felmeres_items, many=True)
            return Response(serializer.data)
        return super().get(request)


class FelmeresItemsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.FelmeresItems.objects.all()
    serializer_class = serializers.FelmeresItemsSerializer
    permission_classes = [AllowAny]


class OfferWebhook(APIView):
    @set_system
    def post(self, request):
        data = json.loads(request.body)
        self.log(
            "Penészmentesítés rendelés webhook meghívva",
            "INFO",
            script_name="pen_offer_webhook",
            details=request.body,
        )
        try:
            if data["Data"]["Felmeresid"] is None:
                return Response("Succesfully received data", status=HTTP_200_OK)

            save_webhook(data["Data"])
            self.save_offer(
                adatlap=models.MiniCrmAdatlapok.objects.get(Id=data["Id"]),
                id=data["Head"]["Id"],
            )
            self.log(
                "Penészmentesítés rendelés webhook sikeresen lefutott",
                "SUCCESS",
                script_name="pen_offer_webhook",
            )
            return Response("Succesfully received data", status=HTTP_200_OK)
        except:
            self.log(
                "Penészmentesítés ajánlat webhook sikertelen",
                "ERROR",
                script_name="pen_offer_webhook",
                details=traceback.format_exc(),
            )
            return Response("Succesfully received data", status=HTTP_200_OK)


class QuestionProductsList(FilterBySystemIdMixin, generics.ListCreateAPIView):
    queryset = models.QuestionProducts.objects.all()
    serializer_class = serializers.QuestionProductsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.query_params.get("product"):
            return (
                super()
                .get_queryset()
                .filter(product=self.request.query_params.get("product"))
            )
        return super().get_queryset()

    def post(self, request):
        data = json.loads(request.body)
        question_instance = models.Questions.objects.get(id=data["question_id"])

        models.QuestionProducts.objects.create(
            question=question_instance, product=data["product_id"]
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
                        product=i,
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
                        product=product_id,
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
    script_name = "pen_unas_get_order"
    minicrm_client = MiniCrmClient(
        script_name=script_name,
    )
    adatlapok = models.MiniCrmAdatlapok.objects.filter(
        Q(Enum1951="Beépítésre vár") | Q(StatusId=3008), CategoryId=29, Deleted="0"
    )
    if not adatlapok.exists():
        return """<?xml version="1.0" encoding="UTF-8" ?>
                            <Orders>
                            </Orders>"""

    datas = []
    for adatlap in adatlapok:
        if adatlap.RendelesSzama != "" and adatlap.RendelesSzama is not None:
            continue
        order_data = models.Orders.objects.get(adatlap_id=adatlap.Id)
        kapcsolat = minicrm_client.contact_details(
            contact_id=adatlap.ContactId,
        )
        if not kapcsolat:
            log(
                "Hiba akadt a kontaktok lekérdezése közben",
                "ERROR",
                script_name,
            )
            return f"<Error></Error>"
        if adatlap.MainContactId != adatlap.ContactId:
            business_kapcsolat = minicrm_client.contact_details(
                contact_id=adatlap.MainContactId,
            )
            if not business_kapcsolat:
                log(
                    "Hiba akadt a kontaktok lekérdezése közben",
                    "ERROR",
                    script_name,
                )
                return f"<Error></Error>"
        else:
            business_kapcsolat = Contact(
                Name=kapcsolat.FullName,
                EUVatNumber="",
                **kapcsolat,
            )

        try:
            cim = minicrm_client.address_details(
                list(
                    minicrm_client.address_ids(
                        adatlap.MainContactId,
                    )
                )[0],
            )
        except:
            ids = list(
                minicrm_client.address_ids(
                    adatlap.ContactId,
                )
            )
            if ids:
                cim = minicrm_client.address_details(ids[0])
            else:
                cim = Address()

        felmeres = models.Felmeresek.objects.filter(
            id=adatlap.FelmeresLink.split("/")[-1] if adatlap.FelmeresLink else 0
        ).first()
        if felmeres is None:
            log("Nem található felmérés", "ERROR", script_name, adatlap.Id)
            continue

        datas.append(
            {
                "OrderData": order_data,
                "AdatlapDetails": adatlap,
                "FelmeresAdatlapDetails": felmeres.adatlap_id,
                "BusinessKapcsolat": business_kapcsolat,
                "Cím": cim,
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
        script_name = "pen_unas_get_order"
        log(
            "Unas rendelések lekérdezése meghívva",
            "INFO",
            script_name,
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
                    "FAILED",
                    script_name,
                )
                return Response(str(e), status=HTTP_401_UNAUTHORIZED)
        return Response("Hibás Token", status=HTTP_401_UNAUTHORIZED)


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


class CancelOffer(MiniCrmAPIView):
    script_name = "pen_cancel_offer"

    def post(self, request):
        self.log(
            "MiniCRM ajánlat sztornózása megkezdődött",
            "INFO",
            request.body.decode("utf-8"),
        )

        adatlap = models.MiniCrmAdatlapok.objects.filter(
            Felmeresid=request.data["adatlap_id"]
        )
        if not adatlap.exists():
            self.log("Nem található adatlap", "ERROR")
            return Response("Nem található adatlap", HTTP_400_BAD_REQUEST)
        offer = models.Offers.objects.filter(adatlap=adatlap.first().Id)
        if not offer.exists():
            self.log("Nem található ajánlat", "ERROR")
            return Response("Nem található ajánlat", HTTP_400_BAD_REQUEST)
        update_resp = self.mini_crm_client.update_offer_order(
            offer_id=offer.first().id,
            fields={"StatusId": "Sztornózva"},
            project=True,
        )
        if update_resp.status_code != 200:
            self.log(
                "MiniCRM ajánlat sztornózása sikertelen",
                "ERROR",
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


class FelmeresNotesList(FilterBySystemAndFelmeresIdMixin, generics.ListCreateAPIView):
    serializer_class = serializers.FelmeresNotesSerializer
    queryset = models.FelmeresekNotes.objects.all()
    permission_classes = [AllowAny]

    def patch(self, request):
        queryset = super().get_queryset()
        data = request.data
        felmeres_id = request.query_params.get("felmeres_id")
        queryset.filter(felmeres_id=felmeres_id).update(**data)
        return Response(status=HTTP_200_OK)


class FelmeresNotesDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.FelmeresNotesSerializer
    queryset = models.FelmeresekNotes.objects.all()
    permission_classes = [AllowAny]


class User(APIView):
    def get(self, _, user):
        try:
            user_role = models.UserRoles.objects.get(user=user)
            user_role_data = {
                "user": user_role.user,
                "role": user_role.role.name,
                "system": user_role.system.system_id,
            }
            return Response(user_role_data)
        except models.UserRoles.DoesNotExist:
            log("Nem található felhasználó", "ERROR", "pen_user_role")
            return Response(status=HTTP_404_NOT_FOUND)


class MiniCrmAdatlapokV2(FilterByQueryParamMixin, generics.ListAPIView):
    pagination_class = PageNumberPagination
    serializer_class = serializers.MiniCrmAdatlapokV2Serializer
    queryset = models.MiniCrmAdatlapokV2.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = [
        "Felmero2",
        "FizetesiMod3",
        "Telepules",
        "CategoryId",
        "Statusz",
    ]
    search_fields = [
        "Name",
        "CategoryId",
        "ContactId",
        "Telepules",
        "Iranyitoszam",
        "Orszag",
        "Felmero2",
        "Cim2",
        "FizetesiMod2",
        "Tavolsag",
        "FelmeresIdopontja2",
        "DateTime1953",
        "FizetesiMod3",
        "RendelesSzama",
        "Total",
        "FelmeresekSzama",
        "Beepitok",
        "Statusz",
    ]
    ordering_fields = "__all__"
    filter_field = "SystemId"
    filter_param = "system_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        felmeres_idopontja = self.request.query_params.get("FelmeresIdopontja2")
        if felmeres_idopontja:
            felmeres_idopontja = json.loads(felmeres_idopontja)
            queryset = queryset.filter(
                FelmeresIdopontja2__gte=datetime.datetime.strptime(
                    felmeres_idopontja["from"], "%Y-%m-%dT%H:%M:%S.%fZ"
                ),
                FelmeresIdopontja2__lte=datetime.datetime.strptime(
                    felmeres_idopontja["to"], "%Y-%m-%dT%H:%M:%S.%fZ"
                ),
            )
        beepites_idopontja = self.request.query_params.get("DateTime1953")
        if beepites_idopontja:
            beepites_idopontja = json.loads(beepites_idopontja)
            queryset = queryset.filter(
                DateTime1953__gte=datetime.datetime.strptime(
                    beepites_idopontja["from"], "%Y-%m-%dT%H:%M:%S.%fZ"
                ),
                DateTime1953__lte=datetime.datetime.strptime(
                    beepites_idopontja["to"], "%Y-%m-%dT%H:%M:%S.%fZ"
                ),
            )
        return queryset


class MiniCrmAdatlapok(FilterByQueryParamMixin, generics.ListAPIView):
    serializer_class = serializers.MiniCrmAdatlapokSerializer
    permission_classes = [AllowAny]
    queryset = models.MiniCrmAdatlapok.objects.all()
    filter_field = "SystemId"
    filter_param = "system_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        id = self.request.query_params.get("Id")
        if id:
            id = id.split(",")
            return queryset.filter(Id__in=id)
        status_id = self.request.query_params.get("StatusId")
        if status_id:
            status_id = status_id.split(",")
            return queryset.filter(StatusId__in=status_id)
        return super().get_queryset()


class MiniCrmAdatlapokDetail(generics.RetrieveAPIView):
    serializer_class = serializers.MiniCrmAdatlapokSerializer
    queryset = models.MiniCrmAdatlapok.objects.all()
    permission_classes = [AllowAny]


class MunkadijList(FilterBySystemIdMixin, generics.ListCreateAPIView):
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


class FelmeresMunkadijList(FilterBySystemIdMixin, generics.ListCreateAPIView):
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
    queryset = models.SystemSettings.objects.all()
    permission_classes = [AllowAny]


# TODO
class MiniCrmProxyId(APIView):
    def put(self, request, adatlap_id):
        log(
            "MiniCRM adatlap frissítése meghívva",
            "INFO",
            "pen_mini_crm_proxy",
            request.data,
        )
        minicrm = MiniCrmClient()
        data = minicrm.update_adatlap_fields(
            id=adatlap_id,
            fields=request.data,
            script_name="pen_mini_crm_proxy",
        )
        if data["code"] == 200:
            log("MiniCRM adatlap frissítése sikeres", "SUCCESS", "pen_mini_crm_proxy")
        else:
            log(
                "MiniCRM adatlap frissítése sikertelen",
                "ERROR",
                "pen_mini_crm_proxy",
                details=data["reason"],
                data={"request_data": request.data, "adatlap_id": adatlap_id},
            )

        if data["code"] == 200:
            return Response(data["data"])
        else:
            return Response(data=data["reason"], status=data["code"])


class GaranciaWebhook(APIView):
    @set_system
    def post(self, request):
        adatlap = json.loads(request.body)
        self.log(
            "Garancia webhook meghívva",
            "INFO",
            script_name="pen_garancia_webhook",
            data=adatlap,
        )
        adatlap = map_wh_fields(
            adatlap, {"BejelentesTipusa", "GaranciaFelmerestVegzi", "FizetesiMod4"}
        )["Data"]
        save_webhook(adatlap, name="garancia")

        if (
            adatlap["StatusId"] == self.get_setting(label="ÚJ BEJELENTÉS").value
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

            response = CalculateDistance(self.system).fn(
                adatlap,
                address=lambda x: x.FullAddress,
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


# TODO
class MiniCrmProxy(MiniCrmAPIView):
    script_name = "pen_minicrm_proxy"

    def post(self, request):
        data = request.body.decode("utf-8")
        self.log(
            "Minicrm proxy meghívva",
            "INFO",
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
                self.log("Minicrm proxy sikeres", "INFO", response.text)
                return Response(response.json())
            else:
                self.log(
                    "Minicrm proxy sikertelen",
                    "ERROR",
                    response.text,
                )
                return Response({"error": "Error " + response.text}, status=400)
        self.log("Minicrm proxy sikertelen", "ERROR", "Missing endpoint")
        return Response({"error": "Missing endpoint"}, status=400)

    def get(self, request):
        endpoint = request.GET.get("endpoint")
        id = request.GET.get("id")

        resp = self.mini_crm_client.get_request(endpoint=endpoint, id=id)
        if not resp.ok:
            self.log(
                "Minicrm proxy sikertelen",
                "ERROR",
                resp.text,
            )
            return Response(resp.text, status=400)

        self.log("Minicrm proxy sikeres", "INFO", resp.json())
        return Response(resp.json())


class CopyFelmeres(APIView):
    def post(self, _, id):
        log("Másolás API meghívva", "INFO", "pen_felmeres_webhook", details=id)
        felmeres = models.Felmeresek.objects.filter(id=id)
        if not felmeres.exists():
            log(
                "Nem található felmérés evvel az azonosítóval",
                "ERROR",
                "pen_felmeres_webhook",
            )
            return Response("Nem található felmérés", status=HTTP_400_BAD_REQUEST)

        felmeres = felmeres.first()
        felmeres.id = None
        felmeres.created_at = datetime.datetime.now()
        felmeres.status = "DRAFT"
        felmeres.name = f"{felmeres.name} - Másolat"

        felmeres.save()

        felmeres_items = models.FelmeresItems.objects.filter(adatlap__id=id)
        if felmeres_items.exists():
            items = []
            for item in felmeres_items:
                item.id = None
                item.adatlap = felmeres
                items.append(item)
            models.FelmeresItems.objects.bulk_create(items)

        felmeres_munkadijak = models.FelmeresMunkadijak.objects.filter(felmeres__id=id)
        if felmeres_munkadijak.exists():
            munkadijak = []
            for munkadij in felmeres_munkadijak:
                munkadij.id = None
                munkadij.felmeres = felmeres
                munkadijak.append(munkadij)
            models.FelmeresMunkadijak.objects.bulk_create(munkadijak)

        felmeres_pictures = models.FelmeresPictures.objects.filter(felmeres__id=id)
        if felmeres_pictures.exists():
            pictures = []
            for picture in felmeres_pictures:
                picture.id = None
                picture.felmeres = felmeres
                pictures.append(picture)
            models.FelmeresPictures.objects.bulk_create(pictures)

        felmeres_notes = models.FelmeresekNotes.objects.filter(felmeres_id=id)
        if felmeres_notes.exists():
            notes = []
            for note in felmeres_notes:
                note.id = None
                note.felmeres_id = felmeres.id
                notes.append(note)
            models.FelmeresekNotes.objects.bulk_create(notes)

        felmeres_questions = models.FelmeresQuestions.objects.filter(adatlap__id=id)
        if felmeres_questions.exists():
            questions = []
            for question in felmeres_questions:
                question.id = None
                question.adatlap = felmeres
                questions.append(question)
            models.FelmeresQuestions.objects.bulk_create(questions)

        return Response(
            serializers.FelmeresekSerializer(felmeres).data, status=HTTP_200_OK
        )


class SalesmenList(FilterBySystemIdMixin, generics.ListCreateAPIView):
    serializer_class = serializers.SalesmenSerializer
    queryset = models.Salesmen.objects.all()
    permission_classes = [AllowAny]
